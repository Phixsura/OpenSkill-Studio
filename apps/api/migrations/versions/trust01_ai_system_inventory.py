"""trust01: AI System Inventory & Risk Classification (ADR-017 Phase 1).

Creates the foundational trust plane tables:
- trust_ai_systems: canonical AI system/capability records
- trust_ai_system_uses: intended and prohibited use cases
- trust_risk_scoring_policies: configurable risk scoring dimensions
- trust_risk_assessments: versioned risk assessments with separation of duty
- trust_audit_events: append-only trust audit trail

Seeds a platform-default risk scoring policy with 8 dimensions.

Revision ID: trust01a00001
Revises: talent15a00015
"""

import json

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from ulid import ULID

revision: str = "trust01a00001"
down_revision: str = "talent15a00015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enums ────────────────────────────────────────────────────────
    trust_system_type = sa.Enum(
        "workflow_pack", "developer_app", "provider_binding",
        "evaluation_pipeline", "skill_pack", "custom",
        name="trust_system_type", create_constraint=True,
    )
    trust_system_lifecycle = sa.Enum(
        "draft", "intake", "under_review", "approved", "deployed",
        "monitoring", "paused", "deprecated", "retired",
        name="trust_system_lifecycle", create_constraint=True,
    )
    trust_risk_tier = sa.Enum(
        "minimal", "low", "medium", "high", "critical",
        name="trust_risk_tier", create_constraint=True,
    )
    trust_use_type = sa.Enum(
        "intended", "prohibited",
        name="trust_use_type", create_constraint=True,
    )
    trust_assessment_status = sa.Enum(
        "draft", "submitted", "approved", "rejected", "superseded",
        name="trust_assessment_status", create_constraint=True,
    )

    # ── trust_ai_systems ─────────────────────────────────────────────
    op.create_table(
        "trust_ai_systems",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("system_type", trust_system_type, nullable=False),
        sa.Column("lifecycle", trust_system_lifecycle, nullable=False, server_default="draft"),
        sa.Column("risk_tier", trust_risk_tier, nullable=True),
        sa.Column("owner_user_id", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("linked_entity_type", sa.String(40), nullable=True),
        sa.Column("linked_entity_id", sa.String(26), nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_trust_system_org_slug", "trust_ai_systems", ["org_id", "slug"], unique=True)
    op.create_index("ix_trust_system_org_lifecycle", "trust_ai_systems", ["org_id", "lifecycle"])
    op.create_index("ix_trust_system_org_type", "trust_ai_systems", ["org_id", "system_type"])
    op.create_index("ix_trust_system_org_risk", "trust_ai_systems", ["org_id", "risk_tier"])
    op.create_index("ix_trust_system_linked", "trust_ai_systems", ["linked_entity_type", "linked_entity_id"])

    # ── trust_ai_system_uses ─────────────────────────────────────────
    op.create_table(
        "trust_ai_system_uses",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("use_type", trust_use_type, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("affected_groups", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("data_classes", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("deployment_contexts", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("regions", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_use_system_type", "trust_ai_system_uses", ["system_id", "use_type"])

    # ── trust_risk_scoring_policies ──────────────────────────────────
    op.create_table(
        "trust_risk_scoring_policies",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("dimensions", postgresql.JSONB, nullable=False),
        sa.Column("tier_thresholds", postgresql.JSONB, nullable=False),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "uq_trust_policy_org_active", "trust_risk_scoring_policies", ["org_id"],
        unique=True, postgresql_where=sa.text("is_active = true"),
    )
    op.create_index("ix_trust_policy_org", "trust_risk_scoring_policies", ["org_id"])

    # ── trust_risk_assessments ───────────────────────────────────────
    op.create_table(
        "trust_risk_assessments",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False),
        sa.Column("policy_id", sa.String(26), sa.ForeignKey("trust_risk_scoring_policies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("status", trust_assessment_status, nullable=False, server_default="draft"),
        sa.Column("dimension_scores", postgresql.JSONB, nullable=False),
        sa.Column("weighted_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("computed_tier", trust_risk_tier, nullable=True),
        sa.Column("override_tier", trust_risk_tier, nullable=True),
        sa.Column("effective_tier", trust_risk_tier, nullable=True),
        sa.Column("justification", sa.Text, nullable=True),
        sa.Column("assessed_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("reviewed_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "assessed_by != reviewed_by OR reviewed_by IS NULL",
            name="ck_trust_assessment_separation_of_duty",
        ),
        sa.CheckConstraint("version >= 1", name="ck_trust_assessment_version_positive"),
    )
    op.create_index("ix_trust_assessment_system_status", "trust_risk_assessments", ["system_id", "status"])
    op.create_index("uq_trust_assessment_system_version", "trust_risk_assessments", ["system_id", "version"], unique=True)

    # ── trust_audit_events ───────────────────────────────────────────
    op.create_table(
        "trust_audit_events",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("actor_user_id", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_type", sa.String(20), nullable=False),
        sa.Column("action", sa.String(60), nullable=False),
        sa.Column("target_type", sa.String(40), nullable=False),
        sa.Column("target_id", sa.String(26), nullable=False),
        sa.Column("before", postgresql.JSONB, nullable=True),
        sa.Column("after", postgresql.JSONB, nullable=True),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("request_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_audit_org_created", "trust_audit_events", ["org_id", "created_at"])
    op.create_index("ix_trust_audit_action", "trust_audit_events", ["action", "created_at"])
    op.create_index("ix_trust_audit_target", "trust_audit_events", ["target_type", "target_id"])

    # ── Seed platform-default scoring policy ─────────────────────────
    dimensions = [
        {"key": "autonomy", "label": "Level of Autonomy", "description": "How independently does the system act?", "weight": 1.0, "scale_min": 1, "scale_max": 5, "guidance": "1=advisory only, 5=fully autonomous"},
        {"key": "data_sensitivity", "label": "Data Sensitivity", "description": "Sensitivity of data the system processes or generates.", "weight": 1.5, "scale_min": 1, "scale_max": 5, "guidance": "1=public data only, 5=highly sensitive"},
        {"key": "impact_reversibility", "label": "Impact & Reversibility", "description": "Severity and reversibility of the system's effects.", "weight": 1.5, "scale_min": 1, "scale_max": 5, "guidance": "1=trivially reversible, 5=fully irreversible"},
        {"key": "tool_access", "label": "Tool & System Access", "description": "Scope of tools, APIs, and systems the AI can invoke.", "weight": 1.0, "scale_min": 1, "scale_max": 5, "guidance": "1=no tool access, 5=admin access"},
        {"key": "blast_radius", "label": "Scale & Blast Radius", "description": "Number of users, tenants, or systems affected.", "weight": 1.2, "scale_min": 1, "scale_max": 5, "guidance": "1=single user, 5=platform-wide"},
        {"key": "uncertainty", "label": "Uncertainty & Confidence", "description": "How uncertain or unpredictable the system's behavior is.", "weight": 1.0, "scale_min": 1, "scale_max": 5, "guidance": "1=deterministic, 5=novel domain"},
        {"key": "eval_coverage", "label": "Evaluation Coverage", "description": "Extent of testing and evaluation evidence available.", "weight": 0.8, "scale_min": 1, "scale_max": 5, "guidance": "1=comprehensive, 5=no evaluation"},
        {"key": "supply_chain", "label": "Supply-Chain Exposure", "description": "Dependency on third-party models, data, or components.", "weight": 1.0, "scale_min": 1, "scale_max": 5, "guidance": "1=fully internal, 5=unvetted external"},
    ]
    thresholds = {"minimal": {"max_score": 1.5}, "low": {"max_score": 2.5}, "medium": {"max_score": 3.5}, "high": {"max_score": 4.5}, "critical": {"min_score": 4.5}}

    op.execute(
        sa.text(
            "INSERT INTO trust_risk_scoring_policies (id, org_id, name, version, is_active, dimensions, tier_thresholds, created_at, updated_at) "
            "VALUES (:id, NULL, :name, 1, true, :dimensions, :thresholds, now(), now())"
        ).bindparams(
            id=str(ULID()),
            name="Platform Default Risk Policy",
            dimensions=json.dumps(dimensions),
            thresholds=json.dumps(thresholds),
        )
    )


def downgrade() -> None:
    op.drop_table("trust_audit_events")
    op.drop_table("trust_risk_assessments")
    op.drop_table("trust_risk_scoring_policies")
    op.drop_table("trust_ai_system_uses")
    op.drop_table("trust_ai_systems")
    op.execute("DROP TYPE IF EXISTS trust_assessment_status")
    op.execute("DROP TYPE IF EXISTS trust_use_type")
    op.execute("DROP TYPE IF EXISTS trust_risk_tier")
    op.execute("DROP TYPE IF EXISTS trust_system_lifecycle")
    op.execute("DROP TYPE IF EXISTS trust_system_type")
