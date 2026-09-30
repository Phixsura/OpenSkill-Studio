"""Experimentation safety vocabulary & gates (ADR-017 §2, Part M).

Structural enforcement of the ethics posture: forbidden targeting keys,
per-domain population-field whitelists, the promotion-target whitelist (which
deliberately contains NO employment action), and the bandit domain gate.
"""

from app.exceptions import AppError

# ── Core vocabularies (pinned; web dropdowns must mirror these) ──────

EXPERIMENT_DOMAINS = frozenset(
    {
        "learning",
        "assessment",
        "workflow",
        "matching",
        "marketplace",
        "operational",
        "talent_flow",
    }
)

EXPERIMENT_STATUSES = frozenset(
    {
        "draft",
        "review",
        "scheduled",
        "running",
        "paused",
        "completed",
        "analyzed",
        "promoted",
        "rejected",
        "archived",
    }
)

TERMINAL_STATUSES = frozenset({"promoted", "rejected", "archived"})

UNIT_TYPES = frozenset(
    {
        "user",
        "cohort",
        "organization",
        "workflow_installation",
        "project",
        "provider_offering",
        "tenant",
    }
)

RISK_CLASSES = frozenset({"low", "medium", "high"})
DESIGNS = frozenset({"parallel", "cluster", "switchback"})
ALLOCATION_MODES = frozenset({"fixed", "bandit"})
STATS_ENGINES = frozenset({"frequentist", "bayesian"})
SEQUENTIAL_METHODS = frozenset({"none", "obrien_fleming", "msprt"})
ANALYSIS_TYPES = frozenset({"randomized", "observational"})
POPULATION_OPS = frozenset({"eq", "in", "not_in", "gte", "lte", "exists"})

# ── Ethics gates (ADR-017 §2) ────────────────────────────────────────

# No population rule may key on a protected/sensitive attribute. Checked as a
# substring-insensitive exact-key match at spec validation time.
FORBIDDEN_TARGETING_KEYS = frozenset(
    {
        "age",
        "date_of_birth",
        "gender",
        "sex",
        "ethnicity",
        "race",
        "religion",
        "disability",
        "nationality",
        "citizenship",
        "sexual_orientation",
        "marital_status",
        "pregnancy",
        "veteran_status",
        "political_affiliation",
        "income",
        "protected_class",
    }
)

# Population rules may only reference these product fields (non-sensitive).
POPULATION_FIELD_WHITELIST = frozenset(
    {
        "user_id",
        "cohort_id",
        "org_id",
        "tenant_id",
        "workflow_installation_id",
        "project_id",
        "provider_offering_id",
        "skill_track",
        "plan_tier",
        "locale",
        "signup_after",
    }
)

# Part K promotion targets. Deliberately NO talent/employment target — an
# experiment result can never draft an offer/hire/reject action (§2.1).
PROMOTION_TARGET_TYPES = frozenset(
    {
        "learning_path",
        "pack_recommendation",
        "workflow_binding",
        "matching_config",
        "eco_rollout_policy",
        "pricing_presentation",
    }
)

# Adaptive allocation is allowed only for presentation-layer, low-risk
# domains; never for learning/assessment/matching/talent_flow (§4.2 v2).
BANDIT_ALLOWED_DOMAINS = frozenset({"marketplace", "operational"})


def check_targeting_field(field: str) -> None:
    """Reject population rules keyed on forbidden or unknown fields."""
    normalized = field.strip().lower()
    if normalized in FORBIDDEN_TARGETING_KEYS:
        raise AppError(
            "EXPERIMENT_FORBIDDEN_TARGETING",
            f"Population rules may not target protected attribute: {field}",
            422,
        )
    if normalized not in POPULATION_FIELD_WHITELIST:
        raise AppError(
            "EXPERIMENT_SPEC_INVALID",
            f"Unknown population field: {field} (allowed: {sorted(POPULATION_FIELD_WHITELIST)})",
            422,
        )


def check_bandit_gate(*, domain: str, risk_class: str, allocation_mode: str) -> None:
    """Thompson-sampling allocation only for low-risk presentation domains."""
    if allocation_mode != "bandit":
        return
    if domain not in BANDIT_ALLOWED_DOMAINS or risk_class != "low":
        raise AppError(
            "EXPERIMENT_BANDIT_DOMAIN_FORBIDDEN",
            "Bandit allocation is only allowed for low-risk marketplace/operational experiments",
            422,
        )
