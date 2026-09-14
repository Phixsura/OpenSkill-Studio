"""Candidate intelligence — alerts, gamification, mentorship, preparation, networking.

Closes gaps: #131-#145 (candidate features).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# ---------------------------------------------------------------------------
# Gap #132: Availability calendar
# ---------------------------------------------------------------------------

AVAILABILITY_MODES = frozenset({
    "available_immediately", "available_from_date", "open_to_offers",
    "not_looking", "available_part_time", "freelance_only",
})


@dataclass(frozen=True, slots=True)
class AvailabilityPreference:
    mode: str
    available_from: datetime | None
    hours_per_week: int | None
    preferred_locations: list[str]
    remote_preference: str  # remote_only, hybrid, on_site, flexible
    notice_period_days: int | None


def validate_availability_preference(pref: dict) -> list[str]:
    errors = []
    mode = pref.get("mode", "")
    if mode and mode not in AVAILABILITY_MODES:
        errors.append(f"Invalid mode. Must be one of: {sorted(AVAILABILITY_MODES)}")
    hours = pref.get("hours_per_week")
    if hours is not None and (hours < 1 or hours > 80):
        errors.append("hours_per_week must be 1-80")
    notice = pref.get("notice_period_days")
    if notice is not None and (notice < 0 or notice > 180):
        errors.append("notice_period_days must be 0-180")
    remote = pref.get("remote_preference", "")
    if remote and remote not in ("remote_only", "hybrid", "on_site", "flexible"):
        errors.append("Invalid remote_preference")
    return errors


# ---------------------------------------------------------------------------
# Gap #133: Job alert preferences
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class JobAlertPreference:
    capability_ids: list[str]
    opportunity_types: list[str]
    location_modes: list[str]
    min_match_score: float
    frequency: str  # instant, daily, weekly


def validate_job_alert(pref: dict) -> list[str]:
    errors = []
    freq = pref.get("frequency", "")
    if freq and freq not in ("instant", "daily", "weekly"):
        errors.append("Frequency must be instant, daily, or weekly")
    score = pref.get("min_match_score", 0)
    if not (0 <= score <= 1):
        errors.append("min_match_score must be 0-1")
    return errors


# ---------------------------------------------------------------------------
# Gap #135: Salary expectation
# ---------------------------------------------------------------------------

CURRENCY_CODES = frozenset({"USD", "EUR", "GBP", "CNY", "JPY", "KRW", "AUD", "CAD"})
PAY_PERIODS = frozenset({"hourly", "monthly", "annual"})


@dataclass(frozen=True, slots=True)
class SalaryExpectation:
    min_amount: float | None
    max_amount: float | None
    currency: str
    pay_period: str
    negotiable: bool


def validate_salary_expectation(exp: dict) -> list[str]:
    errors = []
    currency = exp.get("currency", "USD")
    if currency not in CURRENCY_CODES:
        errors.append(f"Invalid currency. Supported: {sorted(CURRENCY_CODES)}")
    period = exp.get("pay_period", "annual")
    if period not in PAY_PERIODS:
        errors.append(f"Invalid pay_period. Must be one of: {sorted(PAY_PERIODS)}")
    min_a = exp.get("min_amount")
    max_a = exp.get("max_amount")
    if min_a is not None and max_a is not None and min_a > max_a:
        errors.append("min_amount cannot exceed max_amount")
    return errors


# ---------------------------------------------------------------------------
# Gap #140: Mentorship matching
# ---------------------------------------------------------------------------

MENTORSHIP_STATUSES = frozenset({"open", "matched", "active", "completed", "cancelled"})
MENTORSHIP_GOALS = frozenset({
    "career_guidance", "skill_development", "industry_knowledge",
    "leadership", "portfolio_review", "interview_prep", "networking",
})


@dataclass(frozen=True, slots=True)
class MentorshipRequest:
    user_id: str
    role: str  # mentor or mentee
    capability_ids: list[str]
    goals: list[str]
    availability_hours_per_month: int
    preferred_format: str  # video, chat, in_person, flexible


@dataclass(frozen=True, slots=True)
class MentorshipMatch:
    mentor_id: str
    mentee_id: str
    shared_capabilities: list[str]
    compatibility_score: float
    match_reasons: list[str]


def compute_mentorship_compatibility(
    mentor: dict, mentee: dict,
) -> MentorshipMatch:
    """Compute compatibility between a mentor and mentee."""
    mentor_caps = set(mentor.get("capability_ids", []))
    mentee_caps = set(mentee.get("capability_ids", []))
    shared = mentor_caps & mentee_caps

    # Score: shared capabilities + goal alignment + format match
    cap_score = len(shared) / max(len(mentee_caps), 1) if mentee_caps else 0
    goal_overlap = set(mentor.get("goals", [])) & set(mentee.get("goals", []))
    goal_score = len(goal_overlap) / max(len(mentee.get("goals", [])), 1) if mentee.get("goals") else 0
    format_match = 1.0 if mentor.get("preferred_format") == mentee.get("preferred_format") or mentor.get("preferred_format") == "flexible" else 0.5

    score = 0.5 * cap_score + 0.3 * goal_score + 0.2 * format_match

    reasons = []
    if shared:
        reasons.append(f"{len(shared)} shared capabilities")
    if goal_overlap:
        reasons.append(f"Aligned goals: {', '.join(goal_overlap)}")
    if format_match == 1.0:
        reasons.append("Format preference match")

    return MentorshipMatch(
        mentor_id=mentor.get("user_id", ""),
        mentee_id=mentee.get("user_id", ""),
        shared_capabilities=sorted(shared),
        compatibility_score=round(score, 3),
        match_reasons=reasons,
    )


# ---------------------------------------------------------------------------
# Gap #141: Interview preparation tips
# ---------------------------------------------------------------------------

INTERVIEW_PREP_TIPS: dict[str, list[str]] = {
    "technical": [
        "Review the required capabilities listed in the opportunity",
        "Prepare to walk through your most relevant project",
        "Practice explaining your approach to problem-solving",
        "Be ready to discuss specific tools and technologies you've used",
        "Prepare questions about the team and technical stack",
    ],
    "behavioral": [
        "Use the STAR method (Situation, Task, Action, Result)",
        "Prepare 3-4 stories that showcase different competencies",
        "Think about challenges you've overcome and lessons learned",
        "Be specific — use numbers and concrete outcomes",
    ],
    "portfolio": [
        "Select your 3 strongest pieces relevant to the role",
        "Prepare to explain your creative process for each",
        "Be ready to discuss feedback you received and how you iterated",
        "Show range — include different types of work",
    ],
    "general": [
        "Research the company and the interviewer if possible",
        "Prepare thoughtful questions about the role and team",
        "Test your video/audio setup before the interview",
        "Be on time — join 2-3 minutes early",
        "Have a copy of your application and resume ready",
    ],
}


def get_interview_prep(stage_type: str) -> dict:
    """Get interview preparation tips for a specific stage type."""
    tips = INTERVIEW_PREP_TIPS.get(stage_type, INTERVIEW_PREP_TIPS["general"])
    general = INTERVIEW_PREP_TIPS["general"]
    return {
        "stage_type": stage_type,
        "specific_tips": tips,
        "general_tips": general,
        "total_tips": len(tips) + len(general),
    }


# ---------------------------------------------------------------------------
# Gap #142: Progress gamification
# ---------------------------------------------------------------------------

ACHIEVEMENT_TYPES = {
    "first_evidence": {"name": "First Step", "description": "Added your first evidence", "points": 10, "icon": "🎯"},
    "five_capabilities": {"name": "Skill Builder", "description": "Achieved 5+ capabilities", "points": 25, "icon": "⭐"},
    "first_credential": {"name": "Certified", "description": "Earned your first credential", "points": 50, "icon": "🏆"},
    "first_endorsement": {"name": "Peer Recognized", "description": "Received your first endorsement", "points": 15, "icon": "👍"},
    "profile_complete": {"name": "All Star", "description": "Profile completeness 100%", "points": 30, "icon": "💯"},
    "first_application": {"name": "Job Seeker", "description": "Submitted your first application", "points": 20, "icon": "📋"},
    "first_placement": {"name": "Hired!", "description": "Started your first placement", "points": 100, "icon": "🎉"},
    "ten_endorsements": {"name": "Influencer", "description": "Received 10+ endorsements", "points": 50, "icon": "🌟"},
    "learning_streak_7": {"name": "Consistent Learner", "description": "7-day learning streak", "points": 35, "icon": "🔥"},
    "portfolio_builder": {"name": "Show & Tell", "description": "Added 5+ portfolio items", "points": 25, "icon": "🎨"},
}


def check_achievements(user_stats: dict) -> list[dict]:
    """Check which achievements a user has earned based on their stats."""
    earned = []
    checks = {
        "first_evidence": user_stats.get("evidence_count", 0) >= 1,
        "five_capabilities": user_stats.get("capability_count", 0) >= 5,
        "first_credential": user_stats.get("credential_count", 0) >= 1,
        "first_endorsement": user_stats.get("endorsement_count", 0) >= 1,
        "profile_complete": user_stats.get("completeness_score", 0) >= 100,
        "first_application": user_stats.get("application_count", 0) >= 1,
        "first_placement": user_stats.get("placement_count", 0) >= 1,
        "ten_endorsements": user_stats.get("endorsement_count", 0) >= 10,
        "portfolio_builder": user_stats.get("portfolio_count", 0) >= 5,
    }
    for key, achieved in checks.items():
        if achieved and key in ACHIEVEMENT_TYPES:
            earned.append({**ACHIEVEMENT_TYPES[key], "key": key, "earned": True})
    return earned


def compute_total_points(achievements: list[dict]) -> int:
    return sum(a.get("points", 0) for a in achievements)


# ---------------------------------------------------------------------------
# Gap #145: Dark mode preference
# ---------------------------------------------------------------------------

THEME_OPTIONS = frozenset({"system", "light", "dark"})


def validate_theme_preference(theme: str) -> bool:
    return theme in THEME_OPTIONS
