"""trust03: Release Gates & Runtime Guardrails (ADR-017 Phases 3-4).

Creates:
- trust_assurance_profiles: reusable gate templates per trigger
- trust_gate_checks: individual checks within profiles
- trust_gate_results: gate evaluation outcomes per target entity
- trust_guardrail_policies: server-side enforcement policies
- trust_guardrail_evaluations: per-execution check log (append-only)
- trust_action_boundaries: spend ceilings, rate limits, action budgets

Revision ID: trust03a00003
Revises: trust02a00002
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "trust03a00003"
down_revision: str = "trust02a00002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ────────────────────────────────────────────────────────
    trust_gate_trigger = sa.Enum(
        "publish_pack", "approve_app", "install_tenant", "enable_provider",
        "promote_experiment", "increase_autonomy", "accept_federated", "deploy_system",
        name="trust_gate_trigger", create_constraint=True,
    )
    trust_profile_status = sa.Enum(
        "draft", "active", "deprecated",
        name="trust_profile_status", create_constraint=True,
    )
    trust_check_type = sa.Enum(
        "deterministic", "evaluation", "policy", "human_review", "evidence_required",
        name="trust_check_type", create_constraint=True,
    )
    trust_gate_outcome = sa.Enum(
        "pending", "passed", "failed", "skipped", "overridden",
        name="trust_gate_outcome", create_constraint=True,
    )
    trust_guardrail_type = sa.Enum(
        "tool_allowlist", "permission_boundary", "data_loss_prevention",
        "egress_restriction", "output_schema", "action_budget",
        "rate_limit", "spend_ceiling", "human_confirmation", "content_filter",
        name="trust_guardrail_type", create_constraint=True,
    )
    trust_guardrail_status = sa.Enum(
        "draft", "active", "disabled",
        name="trust_guardrail_status", create_constraint=True,
    )
    trust_eval_verdict = sa.Enum(
        "allowed", "blocked", "escalated", "rate_limited",
        name="trust_eval_verdict", create_constraint=True,
    )

    # ── trust_assurance_profiles ─────────────────────────────────────
    op.create_table(
        "trust_assurance_profiles",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("trigger", trust_gate_trigger, nullable=False),
        sa.Column("status", trust_profile_status, nullable=False, server_default="draft"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_profile_org", "trust_assurance_profiles", ["org_id"])
    op.create_index("ix_trust_profile_trigger", "trust_assurance_profiles", ["org_id", "trigger"])

    # ── trust_gate_checks ────────────────────────────────────────────
    op.create_table(
        "trust_gate_checks",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("profile_id", sa.String(26), sa.ForeignKey("trust_assurance_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("check_type", trust_check_type, nullable=False),
        sa.Column("is_blocking", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("ordinal", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_check_profile", "trust_gate_checks", ["profile_id"])

    # ── trust_gate_results ───────────────────────────────────────────
    op.create_table(
        "trust_gate_results",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile_id", sa.String(26), sa.ForeignKey("trust_assurance_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("target_type", sa.String(40), nullable=False),
        sa.Column("target_id", sa.String(26), nullable=False),
        sa.Column("target_version", sa.String(50), nullable=True),
        sa.Column("outcome", trust_gate_outcome, nullable=False, server_default="pending"),
        sa.Column("check_results", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("override_justification", sa.Text, nullable=True),
        sa.Column("override_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("evaluated_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_gate_result_target", "trust_gate_results", ["target_type", "target_id"])
    op.create_index("ix_trust_gate_result_profile", "trust_gate_results", ["profile_id"])
    op.create_index("ix_trust_gate_result_org", "trust_gate_results", ["org_id", "created_at"])

    # ── trust_guardrail_policies ─────────────────────────────────────
    op.create_table(
        "trust_guardrail_policies",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("guardrail_type", trust_guardrail_type, nullable=False),
        sa.Column("status", trust_guardrail_status, nullable=False, server_default="draft"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("config", postgresql.JSONB, nullable=False),
        sa.Column("is_blocking", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("priority", sa.Integer, nullable=False, server_default="100"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_guardrail_org_type", "trust_guardrail_policies", ["org_id", "guardrail_type"])
    op.create_index("ix_trust_guardrail_system", "trust_guardrail_policies", ["system_id"])

    # ── trust_guardrail_evaluations ──────────────────────────────────
    op.create_table(
        "trust_guardrail_evaluations",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("policy_id", sa.String(26), sa.ForeignKey("trust_guardrail_policies.id", ondelete="SET NULL"), nullable=False),
        sa.Column("policy_version", sa.Integer, nullable=False),
        sa.Column("run_id", sa.String(26), nullable=True),
        sa.Column("step_id", sa.String(26), nullable=True),
        sa.Column("system_id", sa.String(26), nullable=True),
        sa.Column("verdict", trust_eval_verdict, nullable=False),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("input_summary", postgresql.JSONB, nullable=True),
        sa.Column("output_summary", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_geval_org_created", "trust_guardrail_evaluations", ["org_id", "created_at"])
    op.create_index("ix_trust_geval_policy", "trust_guardrail_evaluations", ["policy_id"])
    op.create_index("ix_trust_geval_verdict", "trust_guardrail_evaluations", ["verdict"])
    op.create_index("ix_trust_geval_run", "trust_guardrail_evaluations", ["run_id"])

    # ── trust_action_boundaries ──────────────────────────────────────
    op.create_table(
        "trust_action_boundaries",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("boundary_type", sa.String(40), nullable=False),
        sa.Column("limit_value", sa.Integer, nullable=False),
        sa.Column("limit_period", sa.String(20), nullable=True),
        sa.Column("current_usage", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_boundary_org", "trust_action_boundaries", ["org_id"])
    op.create_index("ix_trust_boundary_system", "trust_action_boundaries", ["system_id"])


def downgrade() -> None:
    op.drop_table("trust_action_boundaries")
    op.drop_table("trust_guardrail_evaluations")
    op.drop_table("trust_guardrail_policies")
    op.drop_table("trust_gate_results")
    op.drop_table("trust_gate_checks")
    op.drop_table("trust_assurance_profiles")
    op.execute("DROP TYPE IF EXISTS trust_eval_verdict")
    op.execute("DROP TYPE IF EXISTS trust_guardrail_status")
    op.execute("DROP TYPE IF EXISTS trust_guardrail_type")
    op.execute("DROP TYPE IF EXISTS trust_gate_outcome")
    op.execute("DROP TYPE IF EXISTS trust_check_type")
    op.execute("DROP TYPE IF EXISTS trust_profile_status")
    op.execute("DROP TYPE IF EXISTS trust_gate_trigger")
