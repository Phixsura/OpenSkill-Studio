"""Profile completeness scoring — guides users to build a strong talent profile.

Scoring weights (total = 100):
  has_evidence (any active evidence)           20
  has_credentials (any active credential)      15
  has_preferred_types (opportunity preferences) 10
  discoverable (opted into matching)            15
  has_portfolio (3+ evidence items)             15
  has_availability (set availability status)     5
  has_verified_evidence (non-self-reported)     10
  has_bio (availability_note filled)            10
"""

from __future__ import annotations

from dataclasses import dataclass, field

COMPLETENESS_ITEMS = [
    {
        "key": "has_evidence",
        "label": "Add capability evidence",
        "weight": 20,
        "action": "Record at least one piece of evidence for a capability",
    },
    {
        "key": "has_credentials",
        "label": "Earn a credential",
        "weight": 15,
        "action": "Complete an assessment to earn a verified credential",
    },
    {
        "key": "has_preferred_types",
        "label": "Set opportunity preferences",
        "weight": 10,
        "action": "Choose your preferred opportunity types (internship, job, project, etc.)",
    },
    {
        "key": "discoverable",
        "label": "Enable discoverability",
        "weight": 15,
        "action": "Opt in to be discovered by employers for matching opportunities",
    },
    {
        "key": "has_portfolio",
        "label": "Build your portfolio",
        "weight": 15,
        "action": "Add 3 or more evidence items to demonstrate your skills",
    },
    {
        "key": "has_availability",
        "label": "Set availability",
        "weight": 5,
        "action": "Set your availability status (available, open, busy, etc.)",
    },
    {
        "key": "has_verified_evidence",
        "label": "Get verified evidence",
        "weight": 10,
        "action": "Get evidence verified by an instructor, employer, or peer",
    },
    {
        "key": "has_bio",
        "label": "Add a bio / availability note",
        "weight": 10,
        "action": "Write a short note about your availability or goals",
    },
]

LEVELS = [
    (0, "beginner"),
    (25, "intermediate"),
    (50, "advanced"),
    (75, "expert"),
    (90, "all_star"),
]


@dataclass(frozen=True, slots=True)
class CompletenessResult:
    """Profile completeness assessment."""

    score: float  # 0-100
    level: str  # beginner, intermediate, advanced, expert, all_star
    completed_items: list[str]
    missing_items: list[dict] = field(default_factory=list)


def _determine_level(score: float) -> str:
    """Map score to human-readable level."""
    level = "beginner"
    for threshold, label in LEVELS:
        if score >= threshold:
            level = label
    return level


def compute_profile_completeness(
    *,
    passport: dict | None,
    evidence_count: int,
    credential_count: int,
    has_verified_evidence: bool,
) -> CompletenessResult:
    """Compute profile completeness from passport data and counts.

    Args:
        passport: Passport dict with fields like discoverable, preferred_opportunity_types, etc.
        evidence_count: Total active evidence items for the user
        credential_count: Total active credentials for the user
        has_verified_evidence: Whether user has any non-self-reported evidence

    Returns:
        CompletenessResult with score, level, completed and missing items.
    """
    if passport is None:
        passport = {}

    checks = {
        "has_evidence": evidence_count > 0,
        "has_credentials": credential_count > 0,
        "has_preferred_types": bool(passport.get("preferred_opportunity_types")),
        "discoverable": bool(passport.get("discoverable")),
        "has_portfolio": evidence_count >= 3,
        "has_availability": bool(passport.get("availability_status")),
        "has_verified_evidence": has_verified_evidence,
        "has_bio": bool(passport.get("availability_note")),
    }

    score = 0.0
    completed: list[str] = []
    missing: list[dict] = []

    for item in COMPLETENESS_ITEMS:
        key = item.get("key", "")
        if checks.get(key, False):
            score += item.get("weight", "")
            completed.append(key)
        else:
            missing.append(
                {
                    "key": key,
                    "label": item.get("label", ""),
                    "weight": item.get("weight", ""),
                    "action": item.get("action", ""),
                }
            )

    level = _determine_level(score)
    return CompletenessResult(
        score=round(score, 1),
        level=level,
        completed_items=completed,
        missing_items=missing,
    )
