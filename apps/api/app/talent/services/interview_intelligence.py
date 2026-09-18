"""Interview intelligence — availability, self-scheduling, reminders, panels, no-shows.

Closes gaps: #51-#65 (assessment), #96-#105 (interview & scheduling).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

# ---------------------------------------------------------------------------
# Gap #51: Assessment question bank
# ---------------------------------------------------------------------------

QUESTION_CATEGORIES = frozenset(
    {
        "knowledge",
        "practical",
        "scenario",
        "behavioral",
        "technical",
    }
)


@dataclass(frozen=True, slots=True)
class QuestionBankItem:
    id: str
    category: str
    difficulty: str  # easy, medium, hard
    question_text: str
    capability_ids: list[str]
    expected_answer_hints: str | None
    time_limit_minutes: int | None


def validate_question_bank_item(item: dict) -> list[str]:
    """Execute validate question bank item."""
    errors = []
    if not item.get("question_text") or len(item.get("question_text", "")) < 10:
        errors.append("Question text must be at least 10 characters")
    if item.get("category") and item.get("category", "") not in QUESTION_CATEGORIES:
        errors.append(f"Invalid category. Must be one of: {sorted(QUESTION_CATEGORIES)}")
    if item.get("difficulty") and item.get("difficulty", "") not in ("easy", "medium", "hard"):
        errors.append("Difficulty must be easy, medium, or hard")
    return errors


# ---------------------------------------------------------------------------
# Gap #53: Assessment rubric templates
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RubricTemplate:
    id: str
    name: str
    criteria: list[dict]  # [{name, weight, levels: {1: desc, 2: desc, ...}}]
    total_points: int
    passing_threshold: float


DEFAULT_RUBRIC_TEMPLATES = {
    "technical_interview": {
        "name": "Technical Interview Rubric",
        "criteria": [
            {
                "name": "Problem Solving",
                "weight": 0.3,
                "levels": {
                    1: "Cannot approach",
                    2: "Needs guidance",
                    3: "Independent",
                    4: "Optimal",
                    5: "Innovative",
                },
            },
            {
                "name": "Code Quality",
                "weight": 0.25,
                "levels": {
                    1: "Non-functional",
                    2: "Works but messy",
                    3: "Clean",
                    4: "Well-structured",
                    5: "Exemplary",
                },
            },
            {
                "name": "Communication",
                "weight": 0.2,
                "levels": {
                    1: "Cannot explain",
                    2: "Unclear",
                    3: "Clear",
                    4: "Articulate",
                    5: "Excellent teacher",
                },
            },
            {
                "name": "Domain Knowledge",
                "weight": 0.25,
                "levels": {1: "None", 2: "Basic", 3: "Solid", 4: "Deep", 5: "Expert"},
            },
        ],
        "passing_threshold": 0.6,
    },
    "portfolio_review": {
        "name": "Portfolio Review Rubric",
        "criteria": [
            {"name": "Quality of Work", "weight": 0.35},
            {"name": "Variety & Range", "weight": 0.2},
            {"name": "Presentation", "weight": 0.2},
            {"name": "Relevance to Role", "weight": 0.25},
        ],
        "passing_threshold": 0.5,
    },
}


def get_rubric_template(template_name: str) -> dict | None:
    """Execute get rubric template."""
    return DEFAULT_RUBRIC_TEMPLATES.get(template_name)


def list_rubric_templates() -> list[str]:
    """Execute list rubric templates."""
    return sorted(DEFAULT_RUBRIC_TEMPLATES.keys())


# ---------------------------------------------------------------------------
# Gap #54: Assessment analytics
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AssessmentAnalytics:
    blueprint_id: str
    total_attempts: int
    pass_rate: float
    avg_score: float
    median_score: float
    difficulty_rating: str  # easy (>80% pass), medium (40-80%), hard (<40%)
    avg_completion_minutes: float | None
    score_distribution: dict[str, int]  # {"0-20": 5, "21-40": 10, ...}


def compute_assessment_difficulty(pass_rate: float) -> str:
    """Execute compute assessment difficulty."""
    if pass_rate > 0.80:
        return "easy"
    if pass_rate > 0.40:
        return "medium"
    return "hard"


def compute_score_distribution(scores: list[float]) -> dict[str, int]:
    """Execute compute score distribution."""
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for s in scores:
        pct = s * 100
        if pct <= 20:
            buckets["0-20"] += 1
        elif pct <= 40:
            buckets["21-40"] += 1
        elif pct <= 60:
            buckets["41-60"] += 1
        elif pct <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1
    return buckets


# ---------------------------------------------------------------------------
# Gap #57: Credential verification landing page data
# ---------------------------------------------------------------------------


def build_credential_verification_data(credential: dict, capability: dict | None) -> dict:
    """Build data for a public credential verification page."""
    return {
        "credential_type": credential.get("credential_type", ""),
        "status": credential.get("status", "unknown"),
        "issued_at": credential.get("issued_at"),
        "expires_at": credential.get("expires_at"),
        "is_valid": credential.get("status") == "active",
        "capability_name": capability.get("canonical_name", "") if capability else None,
        "issuer_org_id": credential.get("org_id"),
        "verification_timestamp": datetime.now(UTC).isoformat(),
    }


# ---------------------------------------------------------------------------
# Gap #59: Credential renewal workflow
# ---------------------------------------------------------------------------

RENEWAL_STATUSES = frozenset({"eligible", "in_progress", "renewed", "expired", "not_eligible"})


def check_renewal_eligibility(
    credential: dict,
    renewal_window_days: int = 90,
) -> dict:
    """Check if a credential is eligible for renewal."""
    expires_at = credential.get("expires_at") or credential.get("revalidation_at")
    if not expires_at:
        return {"eligible": False, "reason": "No expiration date set", "status": "not_eligible"}

    if isinstance(expires_at, str):
        try:
            try:
                expires_at = datetime.fromisoformat(expires_at)

            except (ValueError, TypeError):
                expires_at = None
        except (ValueError, TypeError):
            return {
                "eligible": False,
                "reason": "Invalid expiration date",
                "status": "not_eligible",
            }

    now = datetime.now(UTC)
    window_start = expires_at - timedelta(days=renewal_window_days)

    if now < window_start:
        days_until = (window_start - now).days
        return {
            "eligible": False,
            "reason": f"Renewal window opens in {days_until} days",
            "status": "not_eligible",
        }

    if now > expires_at:
        return {
            "eligible": True,
            "reason": "Credential has expired — renewal required",
            "status": "expired",
        }

    days_remaining = (expires_at - now).days
    return {
        "eligible": True,
        "reason": f"Expires in {days_remaining} days — eligible for renewal",
        "status": "eligible",
    }


# ---------------------------------------------------------------------------
# Gap #97: Interviewer availability
# ---------------------------------------------------------------------------

DAYS_OF_WEEK = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


@dataclass(frozen=True, slots=True)
class AvailabilitySlot:
    day: str
    start_hour: int  # 0-23
    end_hour: int  # 0-23
    timezone: str


def validate_availability(slots: list[dict]) -> list[str]:
    """Execute validate availability."""
    errors = []
    for i, s in enumerate(slots):
        day = s.get("day", "").lower()
        if day not in DAYS_OF_WEEK:
            errors.append(f"Slot {i}: invalid day '{day}'")
        start = s.get("start_hour", -1)
        end = s.get("end_hour", -1)
        if not (0 <= start <= 23) or not (0 <= end <= 23):
            errors.append(f"Slot {i}: hours must be 0-23")
        if start >= end:
            errors.append(f"Slot {i}: start_hour must be before end_hour")
    return errors


# ---------------------------------------------------------------------------
# Gap #98: Self-scheduling booking links
# ---------------------------------------------------------------------------


def generate_booking_link(
    interview_stage_id: str,
    base_url: str = "https://openskill.studio",
) -> dict:
    """Generate a booking link for candidate self-scheduling."""
    import hashlib

    token = hashlib.sha256(f"book:{interview_stage_id}".encode()).hexdigest()[:16]
    url = f"{base_url}/book/{token}"
    return {"url": url, "token": token, "interview_stage_id": interview_stage_id}


# ---------------------------------------------------------------------------
# Gap #99: Interview reminders
# ---------------------------------------------------------------------------


def compute_reminder_schedule(
    interview_time: datetime,
) -> list[dict]:
    """Compute when to send interview reminders."""
    reminders = []
    now = datetime.now(UTC)

    # 24 hours before
    t24 = interview_time - timedelta(hours=24)
    if t24 > now:
        reminders.append(
            {
                "type": "24h_before",
                "send_at": t24.isoformat(),
                "message": "Your interview is tomorrow",
            }
        )

    # 1 hour before
    t1 = interview_time - timedelta(hours=1)
    if t1 > now:
        reminders.append(
            {
                "type": "1h_before",
                "send_at": t1.isoformat(),
                "message": "Your interview starts in 1 hour",
            }
        )

    # 15 minutes before
    t15 = interview_time - timedelta(minutes=15)
    if t15 > now:
        reminders.append(
            {
                "type": "15m_before",
                "send_at": t15.isoformat(),
                "message": "Your interview starts in 15 minutes",
            }
        )

    return reminders


# ---------------------------------------------------------------------------
# Gap #104: Interview no-show tracking
# ---------------------------------------------------------------------------

NO_SHOW_STATUSES = frozenset(
    {"attended", "no_show_candidate", "no_show_interviewer", "cancelled", "rescheduled"}
)


def classify_attendance(
    scheduled_time: datetime,
    actual_join_time: datetime | None,
    grace_minutes: int = 15,
) -> str:
    """Classify interview attendance."""
    if actual_join_time is None:
        # Check if past grace period
        if datetime.now(UTC) > scheduled_time + timedelta(minutes=grace_minutes):
            return "no_show_candidate"
        return "pending"
    delay = (actual_join_time - scheduled_time).total_seconds() / 60
    if delay > grace_minutes:
        return "late"
    return "attended"


# ---------------------------------------------------------------------------
# Gap #102: Interview debrief
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DebriefSummary:
    interview_stage_id: str
    total_scorecards: int
    avg_overall_rating: float | None
    recommendation_breakdown: dict[str, int]
    consensus: str  # unanimous_hire, unanimous_no_hire, mixed, insufficient


def compute_debrief_summary(scorecards: list[dict]) -> DebriefSummary:
    """Compute debrief summary from interviewer scorecards."""
    if not scorecards:
        return DebriefSummary("", 0, None, {}, "insufficient")

    ratings = [s.get("overall_rating") for s in scorecards if s.get("overall_rating")]
    avg = sum(ratings) / len(ratings) if ratings else None

    recs: dict[str, int] = {}
    for s in scorecards:
        rec = s.get("recommendation", "no_response")
        recs[rec] = recs.get(rec, 0) + 1

    # Consensus
    if len(recs) == 1:
        sole_rec = list(recs.keys())[0]
        if sole_rec in ("strong_hire", "hire"):
            consensus = "unanimous_hire"
        elif sole_rec in ("no_hire", "strong_no_hire"):
            consensus = "unanimous_no_hire"
        else:
            consensus = "mixed"
    elif len(scorecards) < 2:
        consensus = "insufficient"
    else:
        consensus = "mixed"

    return DebriefSummary(
        interview_stage_id=scorecards[0].get("interview_stage_id", ""),
        total_scorecards=len(scorecards),
        avg_overall_rating=round(avg, 2) if avg else None,
        recommendation_breakdown=recs,
        consensus=consensus,
    )
