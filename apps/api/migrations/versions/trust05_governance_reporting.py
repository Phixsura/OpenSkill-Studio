"""trust05: Governance Templates & Compliance Reporting (ADR-017 Phase 6).

Creates:
- trust_governance_templates: reusable governance profiles with inheritance
- trust_compliance_reports: generated report snapshots
- trust_tenant_policies: per-tenant policy overrides

Revision ID: trust05a00005
Revises: trust04a00004
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "trust05a00005"
down_revision: str = "trust04a00004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    trust_template_scope = sa.Enum(
        "global", "region", "tenant", "capability_class", "deployment_type",
        name="trust_template_scope", create_constraint=True,
    )
    trust_template_status = sa.Enum(
        "draft", "active", "deprecated",
        name="trust_template_status", create_constraint=True,
    )
    trust_report_type = sa.Enum(
        "system_inventory", "risk_assessments", "approval_history", "assurance_cases",
        "evidence_gaps", "evaluation_results", "data_flow_summary", "human_oversight",
        "incident_summary", "exception_log", "full_compliance",
        name="trust_report_type", create_constraint=True,
    )
    trust_report_status = sa.Enum(
        "generating", "completed", "failed",
        name="trust_report_status", create_constraint=True,
    )
    trust_policy_override_type = sa.Enum(
        "risk_threshold", "gate_requirement", "guardrail_config", "review_requirement",
        "monitoring_config", "data_residency", "retention_policy",
        name="trust_policy_override_type", create_constraint=True,
    )

    # ── trust_governance_templates ───────────────────────────────────
    op.create_table(
        "trust_governance_templates",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("scope", trust_template_scope, nullable=False),
        sa.Column("scope_value", sa.String(100), nullable=True),
        sa.Column("status", trust_template_status, nullable=False, server_default="draft"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("config", postgresql.JSONB, nullable=False),
        sa.Column("parent_template_id", sa.String(26), sa.ForeignKey("trust_governance_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_restrictive", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_template_org", "trust_governance_templates", ["org_id"])
    op.create_index("ix_trust_template_scope", "trust_governance_templates", ["scope"])
    op.create_index("ix_trust_template_status", "trust_governance_templates", ["status"])

    # ── trust_compliance_reports ─────────────────────────────────────
    op.create_table(
        "trust_compliance_reports",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_type", trust_report_type, nullable=False),
        sa.Column("status", trust_report_status, nullable=False, server_default="generating"),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("content", postgresql.JSONB, nullable=True),
        sa.Column("filters", postgresql.JSONB, nullable=True),
        sa.Column("system_count", sa.Integer, nullable=True),
        sa.Column("finding_count", sa.Integer, nullable=True),
        sa.Column("generated_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_report_org", "trust_compliance_reports", ["org_id"])
    op.create_index("ix_trust_report_type", "trust_compliance_reports", ["org_id", "report_type"])
    op.create_index("ix_trust_report_created", "trust_compliance_reports", ["org_id", "created_at"])

    # ── trust_tenant_policies ────────────────────────────────────────
    op.create_table(
        "trust_tenant_policies",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("override_type", trust_policy_override_type, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("config", postgresql.JSONB, nullable=False),
        sa.Column("template_id", sa.String(26), sa.ForeignKey("trust_governance_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_tenant_policy_org", "trust_tenant_policies", ["org_id"])
    op.create_index("ix_trust_tenant_policy_type", "trust_tenant_policies", ["org_id", "override_type"])


def downgrade() -> None:
    op.drop_table("trust_tenant_policies")
    op.drop_table("trust_compliance_reports")
    op.drop_table("trust_governance_templates")
    op.execute("DROP TYPE IF EXISTS trust_policy_override_type")
    op.execute("DROP TYPE IF EXISTS trust_report_status")
    op.execute("DROP TYPE IF EXISTS trust_report_type")
    op.execute("DROP TYPE IF EXISTS trust_template_status")
    op.execute("DROP TYPE IF EXISTS trust_template_scope")
