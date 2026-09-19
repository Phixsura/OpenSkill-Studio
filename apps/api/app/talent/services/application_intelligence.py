"""Application pipeline intelligence — form builder, screening, batch ops, timeline.

Closes gaps: #51-#55 (assessment gaps handled separately),
#81 (form builder), #82 (auto-screening), #84 (candidate notes),
#85 (withdrawal reasons), #86 (timeline), #87 (batch actions),
#90 (reference checks), #91 (score ranking), #92 (stage time limits).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

# ---------------------------------------------------------------------------
# Gap #81: Application form builder
# ---------------------------------------------------------------------------

QUESTION_TYPES = frozenset(
    {
        "text",
        "textarea",
        "select",
        "multiselect",
        "yes_no",
        "number",
        "date",
        "file_upload",
        "url",
    }
)


@dataclass(frozen=True, slots=True)
class CustomQuestion:
    id: str
    question_text: str
    question_type: str
    required: bool
    options: list[str]  # for select/multiselect
    max_length: int | None


def validate_custom_questions(questions: list[dict]) -> list[str]:
    """Validate custom application questions."""
    errors = []
    if len(questions) > 20:
        errors.append("Maximum 20 custom questions per opportunity")
    for i, q in enumerate(questions):
        if not q.get("question_text"):
            errors.append(f"Question {i}: text is required")
        qt = q.get("question_type", "text")
        if qt not in QUESTION_TYPES:
            errors.append(f"Question {i}: invalid type '{qt}'")
        if qt in ("select", "multiselect") and not q.get("options"):
            errors.append(f"Question {i}: options required for {qt}")
    return errors


# ---------------------------------------------------------------------------
# Gap #82: Auto-screening rules
# ---------------------------------------------------------------------------

SCREENING_RULE_TYPES = frozenset(
    {
        "min_capability_level",
        "required_credential",
        "min_evidence_count",
        "min_endorsements",
        "required_verification_level",
        "keyword_match",
    }
)


@dataclass(frozen=True, slots=True)
class ScreeningRule:
    rule_type: str
    field: str
    operator: str  # >=, ==, contains, exists
    value: str | int | float
    action: str  # pass, fail, flag_for_review


def evaluate_screening_rules(
    rules: list[dict],
    candidate_data: dict,
) -> dict:
    """Evaluate auto-screening rules against candidate data.

    Returns: {passed: bool, results: [{rule, passed, reason}], score: float}
    """
    if not rules:
        return {"passed": True, "results": [], "score": 1.0}

    results = []
    passed_count = 0
    for rule in rules:
        rule_type = rule.get("rule_type", "")
        value = rule.get("value")
        field = rule.get("field", "")

        candidate_value = candidate_data.get(field, candidate_data.get(rule_type))
        rule_passed = False

        op = rule.get("operator", ">=")
        if op == ">=" and candidate_value is not None:
            try:
                rule_passed = float(candidate_value) >= float(value)
            except (TypeError, ValueError):
                rule_passed = False
        elif op == "==" and candidate_value is not None:
            rule_passed = str(candidate_value) == str(value)
        elif op == "contains" and isinstance(candidate_value, str):
            rule_passed = str(value).lower() in candidate_value.lower()
        elif op == "exists":
            rule_passed = candidate_value is not None

        if rule_passed:
            passed_count += 1

        results.append(
            {
                "rule_type": rule_type,
                "field": field,
                "passed": rule_passed,
                "action": rule.get("action", "pass"),
            }
        )

    score = passed_count / max(len(rules), 1) if rules else 1.0
    all_passed = all(r["passed"] or r["action"] == "flag_for_review" for r in results)

    return {"passed": all_passed, "results": results, "score": round(score, 3)}


# ---------------------------------------------------------------------------
# Gap #85: Withdrawal reasons
# ---------------------------------------------------------------------------

WITHDRAWAL_REASONS = frozenset(
    {
        "accepted_other_offer",
        "compensation_mismatch",
        "role_not_fit",
        "location_issue",
        "timing_issue",
        "personal_reasons",
        "company_culture",
        "better_opportunity",
        "other",
    }
)


def validate_withdrawal_reason(reason: str) -> bool:
    """Execute validate withdrawal reason."""
    return reason in WITHDRAWAL_REASONS


# ---------------------------------------------------------------------------
# Gap #86: Application timeline
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    stage: str
    timestamp: datetime
    actor: str | None
    note: str | None
    duration_from_previous_hours: float | None


def build_application_timeline(events: list[dict]) -> list[TimelineEvent]:
    """Build a detailed timeline from application events."""
    if not events:
        return []

    sorted_events = sorted(events, key=lambda e: e.get("timestamp", ""))
    timeline = []

    for i, ev in enumerate(sorted_events):
        ts = ev.get("timestamp")
        if isinstance(ts, str):
            try:
                try:
                    ts = datetime.fromisoformat(ts)
                except (ValueError, TypeError):
                    ts = None
            except (ValueError, TypeError):
                ts = None

        prev_ts = None
        if i > 0 and timeline:
            prev_ts = timeline[-1].timestamp

        duration = None
        if ts and prev_ts:
            duration = round((ts - prev_ts).total_seconds() / 3600, 1)

        timeline.append(
            TimelineEvent(
                stage=ev.get("to_status", ev.get("stage", "")),
                timestamp=ts or datetime.now(UTC),
                actor=ev.get("acted_by"),
                note=ev.get("note"),
                duration_from_previous_hours=duration,
            )
        )

    return timeline


# ---------------------------------------------------------------------------
# Gap #87: Batch actions
# ---------------------------------------------------------------------------

BATCH_ACTIONS = frozenset({"advance", "reject", "archive", "restore"})
MAX_BATCH_SIZE = 50


def validate_batch_action(action: str, app_ids: list[str]) -> list[str]:
    """Validate a batch action request."""
    errors = []
    if action not in BATCH_ACTIONS:
        errors.append(f"Invalid action '{action}'. Must be one of: {sorted(BATCH_ACTIONS)}")
    if not app_ids:
        errors.append("At least one application ID required")
    if len(app_ids) > MAX_BATCH_SIZE:
        errors.append(f"Maximum {MAX_BATCH_SIZE} applications per batch")
    if len(set(app_ids)) != len(app_ids):
        errors.append("Duplicate application IDs not allowed")
    return errors


# ---------------------------------------------------------------------------
# Gap #90: Reference checks
# ---------------------------------------------------------------------------

REFERENCE_STATUSES = frozenset({"requested", "submitted", "verified", "expired"})


@dataclass(frozen=True, slots=True)
class ReferenceCheck:
    id: str
    application_id: str
    referee_name: str
    referee_email: str
    referee_relationship: str
    status: str
    submitted_at: datetime | None


def validate_reference(ref: dict) -> list[str]:
    """Validate a reference check submission."""
    errors = []
    if not ref.get("referee_name"):
        errors.append("Referee name is required")
    email = ref.get("referee_email", "")
    if not email or "@" not in email:
        errors.append("Valid referee email is required")
    if not ref.get("referee_relationship"):
        errors.append("Relationship to referee is required")
    return errors


# ---------------------------------------------------------------------------
# Gap #92: Stage time limits
# ---------------------------------------------------------------------------

DEFAULT_STAGE_LIMITS_DAYS: dict[str, int] = {
    "screening": 7,
    "interview": 14,
    "assessment": 10,
    "offer": 7,
}


def check_stage_overdue(
    current_stage: str,
    stage_entered_at: datetime,
    custom_limits: dict[str, int] | None = None,
) -> dict:
    """Check if an application has exceeded its stage time limit."""
    limits = custom_limits or DEFAULT_STAGE_LIMITS_DAYS
    limit_days = limits.get(current_stage)

    if limit_days is None:
        return {"overdue": False, "limit_days": None, "days_in_stage": None}

    now = datetime.now(UTC)
    days_in = (now - stage_entered_at).days
    overdue = days_in > limit_days

    return {
        "overdue": overdue,
        "limit_days": limit_days,
        "days_in_stage": days_in,
        "days_remaining": max(0, limit_days - days_in),
    }
