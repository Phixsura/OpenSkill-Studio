"""trust06: Threats, Privacy & Change Management (ADR-017 Parts E, G, K).

Creates:
- trust_threat_models: reusable threat models
- trust_redteam_suites: adversarial test suites with fixtures
- trust_redteam_runs: test execution records
- trust_redteam_findings: individual findings from runs
- trust_privacy_reviews: privacy reviews for AI data flows
- trust_consent_records: consent/legal-basis references
- trust_change_events: assurance-changing events with impact analysis

Revision ID: trust06a00006
Revises: trust05a00005
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "trust06a00006"
down_revision: str = "trust05a00005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ────────────────────────────────────────────────────────
    trust_threat_category = sa.Enum(
        "prompt_injection", "indirect_instruction", "data_exfiltration",
        "cross_tenant_leakage", "unsafe_tool_invocation", "privilege_escalation",
        "compromised_component", "dependency_tampering", "untrusted_output",
        "model_drift", "automation_abuse", "custom",
        name="trust_threat_category", create_constraint=True,
    )
    trust_threat_severity = sa.Enum(
        "info", "low", "medium", "high", "critical",
        name="trust_threat_severity", create_constraint=True,
    )
    trust_testrun_status = sa.Enum(
        "pending", "running", "completed", "failed", "cancelled",
        name="trust_testrun_status", create_constraint=True,
    )
    trust_finding_status = sa.Enum(
        "open", "mitigated", "accepted", "false_positive", "fixed",
        name="trust_finding_status", create_constraint=True,
    )
    trust_privacy_review_status = sa.Enum(
        "draft", "in_review", "approved", "rejected", "requires_changes",
        name="trust_privacy_review_status", create_constraint=True,
    )
    trust_data_classification = sa.Enum(
        "public", "internal", "confidential", "sensitive_pii", "highly_sensitive",
        name="trust_data_classification", create_constraint=True,
    )
    trust_legal_basis = sa.Enum(
        "consent", "contract", "legal_obligation", "vital_interest",
        "public_interest", "legitimate_interest",
        name="trust_legal_basis", create_constraint=True,
    )
    trust_consent_status = sa.Enum(
        "granted", "denied", "withdrawn", "not_required",
        name="trust_consent_status", create_constraint=True,
    )
    trust_change_type = sa.Enum(
        "model_version", "provider_version", "prompt_template", "tool_permission",
        "component_dependency", "data_source", "evaluation_method",
        "intended_use", "deployment_scale", "configuration",
        name="trust_change_type", create_constraint=True,
    )
    trust_change_impact = sa.Enum(
        "none", "low", "medium", "high", "requires_revalidation",
        name="trust_change_impact", create_constraint=True,
    )
    trust_revalidation_status = sa.Enum(
        "pending", "in_progress", "completed", "skipped",
        name="trust_revalidation_status", create_constraint=True,
    )

    # ── trust_threat_models ──────────────────────────────────────────
    op.create_table(
        "trust_threat_models",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", trust_threat_category, nullable=False),
        sa.Column("attack_vectors", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("preconditions", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("mitigations", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("affected_components", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("severity", trust_threat_severity, nullable=False, server_default="medium"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_threat_org", "trust_threat_models", ["org_id"])
    op.create_index("ix_trust_threat_category", "trust_threat_models", ["category"])
    op.create_index("ix_trust_threat_system", "trust_threat_models", ["system_id"])

    # ── trust_redteam_suites ─────────────────────────────────────────
    op.create_table(
        "trust_redteam_suites",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("threat_model_id", sa.String(26), sa.ForeignKey("trust_threat_models.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("fixtures", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("isolation_config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("test_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_redteam_org", "trust_redteam_suites", ["org_id"])
    op.create_index("ix_trust_redteam_threat", "trust_redteam_suites", ["threat_model_id"])

    # ── trust_redteam_runs ───────────────────────────────────────────
    op.create_table(
        "trust_redteam_runs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("suite_id", sa.String(26), sa.ForeignKey("trust_redteam_suites.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), nullable=True),
        sa.Column("status", trust_testrun_status, nullable=False, server_default="pending"),
        sa.Column("results", postgresql.JSONB, nullable=True),
        sa.Column("total_tests", sa.Integer, nullable=False, server_default="0"),
        sa.Column("passed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("started_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_rtrun_org", "trust_redteam_runs", ["org_id", "created_at"])
    op.create_index("ix_trust_rtrun_suite", "trust_redteam_runs", ["suite_id"])
    op.create_index("ix_trust_rtrun_status", "trust_redteam_runs", ["status"])

    # ── trust_redteam_findings ───────────────────────────────────────
    op.create_table(
        "trust_redteam_findings",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("run_id", sa.String(26), sa.ForeignKey("trust_redteam_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("severity", trust_threat_severity, nullable=False),
        sa.Column("status", trust_finding_status, nullable=False, server_default="open"),
        sa.Column("category", sa.String(60), nullable=True),
        sa.Column("exploit_detail", postgresql.JSONB, nullable=True),
        sa.Column("affected_versions", postgresql.JSONB, nullable=True),
        sa.Column("mitigation", sa.Text, nullable=True),
        sa.Column("regression_test_id", sa.String(26), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_rtfinding_run", "trust_redteam_findings", ["run_id"])
    op.create_index("ix_trust_rtfinding_severity", "trust_redteam_findings", ["severity"])
    op.create_index("ix_trust_rtfinding_status", "trust_redteam_findings", ["status"])

    # ── trust_privacy_reviews ────────────────────────────────────────
    op.create_table(
        "trust_privacy_reviews",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("status", trust_privacy_review_status, nullable=False, server_default="draft"),
        sa.Column("data_inputs", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("data_outputs", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("data_classification", trust_data_classification, nullable=False, server_default="internal"),
        sa.Column("purpose_limitation", sa.Text, nullable=True),
        sa.Column("minimization_measures", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("redaction_config", postgresql.JSONB, nullable=True),
        sa.Column("retention_policy", postgresql.JSONB, nullable=True),
        sa.Column("legal_basis", trust_legal_basis, nullable=True),
        sa.Column("legal_basis_detail", sa.Text, nullable=True),
        sa.Column("regions", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("cross_region_transfers", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("provider_data_use", postgresql.JSONB, nullable=True),
        sa.Column("reviewed_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_privacy_org", "trust_privacy_reviews", ["org_id"])
    op.create_index("ix_trust_privacy_system", "trust_privacy_reviews", ["system_id"])
    op.create_index("ix_trust_privacy_status", "trust_privacy_reviews", ["status"])

    # ── trust_consent_records ────────────────────────────────────────
    op.create_table(
        "trust_consent_records",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("purpose", sa.String(300), nullable=False),
        sa.Column("consent_status", trust_consent_status, nullable=False),
        sa.Column("data_categories", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_consent_org", "trust_consent_records", ["org_id"])
    op.create_index("ix_trust_consent_system", "trust_consent_records", ["system_id"])
    op.create_index("ix_trust_consent_status", "trust_consent_records", ["consent_status"])

    # ── trust_change_events ──────────────────────────────────────────
    op.create_table(
        "trust_change_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("change_type", trust_change_type, nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("before_value", postgresql.JSONB, nullable=True),
        sa.Column("after_value", postgresql.JSONB, nullable=True),
        sa.Column("impact", trust_change_impact, nullable=False, server_default="pending"),
        sa.Column("affected_evidence", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("affected_assessments", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("requires_revalidation", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("revalidation_status", trust_revalidation_status, nullable=False, server_default="pending"),
        sa.Column("revalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revalidated_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("detected_by", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_change_org", "trust_change_events", ["org_id", "created_at"])
    op.create_index("ix_trust_change_system", "trust_change_events", ["system_id"])
    op.create_index("ix_trust_change_type", "trust_change_events", ["change_type"])
    op.create_index("ix_trust_change_impact", "trust_change_events", ["impact"])


def downgrade() -> None:
    op.drop_table("trust_change_events")
    op.drop_table("trust_consent_records")
    op.drop_table("trust_privacy_reviews")
    op.drop_table("trust_redteam_findings")
    op.drop_table("trust_redteam_runs")
    op.drop_table("trust_redteam_suites")
    op.drop_table("trust_threat_models")
    op.execute("DROP TYPE IF EXISTS trust_revalidation_status")
    op.execute("DROP TYPE IF EXISTS trust_change_impact")
    op.execute("DROP TYPE IF EXISTS trust_change_type")
    op.execute("DROP TYPE IF EXISTS trust_consent_status")
    op.execute("DROP TYPE IF EXISTS trust_legal_basis")
    op.execute("DROP TYPE IF EXISTS trust_data_classification")
    op.execute("DROP TYPE IF EXISTS trust_privacy_review_status")
    op.execute("DROP TYPE IF EXISTS trust_finding_status")
    op.execute("DROP TYPE IF EXISTS trust_testrun_status")
    op.execute("DROP TYPE IF EXISTS trust_threat_severity")
    op.execute("DROP TYPE IF EXISTS trust_threat_category")
