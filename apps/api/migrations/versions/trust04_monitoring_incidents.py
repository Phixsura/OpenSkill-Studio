"""trust04: Monitoring & Incidents (ADR-017 Phase 5).

Creates:
- trust_monitors: configured monitors per system
- trust_monitor_alerts: triggered alert log
- trust_incidents: incident lifecycle records
- trust_incident_actions: remediation action log

Revision ID: trust04a00004
Revises: trust03a00003
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "trust04a00004"
down_revision: str = "trust03a00003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    trust_monitor_type = sa.Enum(
        "quality_regression", "safety_regression", "behavior_drift", "guardrail_rate",
        "cost_anomaly", "latency_anomaly", "evidence_expiry", "dependency_change",
        "privacy_incident", "custom",
        name="trust_monitor_type", create_constraint=True,
    )
    trust_monitor_status = sa.Enum(
        "active", "paused", "disabled",
        name="trust_monitor_status", create_constraint=True,
    )
    trust_alert_severity = sa.Enum(
        "info", "warning", "critical",
        name="trust_alert_severity", create_constraint=True,
    )
    trust_alert_status = sa.Enum(
        "open", "acknowledged", "resolved", "suppressed",
        name="trust_alert_status", create_constraint=True,
    )
    trust_incident_severity = sa.Enum(
        "low", "medium", "high", "critical",
        name="trust_incident_severity", create_constraint=True,
    )
    trust_incident_status = sa.Enum(
        "reported", "triaging", "contained", "investigating",
        "remediating", "validating", "closed",
        name="trust_incident_status", create_constraint=True,
    )
    trust_incident_action_type = sa.Enum(
        "pause_capability", "revoke_app", "disable_provider", "rollback_release",
        "restrict_permissions", "containment", "investigation", "remediation",
        "validation", "communication", "post_incident",
        name="trust_incident_action_type", create_constraint=True,
    )
    trust_incident_action_status = sa.Enum(
        "pending", "in_progress", "completed", "failed", "cancelled",
        name="trust_incident_action_status", create_constraint=True,
    )

    # ── trust_monitors ───────────────────────────────────────────────
    op.create_table(
        "trust_monitors",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("monitor_type", trust_monitor_type, nullable=False),
        sa.Column("status", trust_monitor_status, nullable=False, server_default="active"),
        sa.Column("config", postgresql.JSONB, nullable=False),
        sa.Column("alert_severity", trust_alert_severity, nullable=False, server_default="warning"),
        sa.Column("check_interval_minutes", sa.Integer, nullable=False, server_default="60"),
        sa.Column("created_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_monitor_org", "trust_monitors", ["org_id"])
    op.create_index("ix_trust_monitor_system", "trust_monitors", ["system_id"])
    op.create_index("ix_trust_monitor_type", "trust_monitors", ["org_id", "monitor_type"])

    # ── trust_monitor_alerts ─────────────────────────────────────────
    op.create_table(
        "trust_monitor_alerts",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), nullable=False),
        sa.Column("monitor_id", sa.String(26), sa.ForeignKey("trust_monitors.id", ondelete="SET NULL"), nullable=False),
        sa.Column("system_id", sa.String(26), nullable=True),
        sa.Column("severity", trust_alert_severity, nullable=False),
        sa.Column("status", trust_alert_status, nullable=False, server_default="open"),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("metric_value", postgresql.JSONB, nullable=True),
        sa.Column("threshold", postgresql.JSONB, nullable=True),
        sa.Column("incident_id", sa.String(26), nullable=True),
        sa.Column("acknowledged_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_alert_org_created", "trust_monitor_alerts", ["org_id", "created_at"])
    op.create_index("ix_trust_alert_monitor", "trust_monitor_alerts", ["monitor_id"])
    op.create_index("ix_trust_alert_severity_status", "trust_monitor_alerts", ["severity", "status"])

    # ── trust_incidents ──────────────────────────────────────────────
    op.create_table(
        "trust_incidents",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("system_id", sa.String(26), sa.ForeignKey("trust_ai_systems.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("severity", trust_incident_severity, nullable=False),
        sa.Column("status", trust_incident_status, nullable=False, server_default="reported"),
        sa.Column("impact", postgresql.JSONB, nullable=True),
        sa.Column("affected_tenants", postgresql.JSONB, nullable=True),
        sa.Column("affected_versions", postgresql.JSONB, nullable=True),
        sa.Column("root_cause", sa.Text, nullable=True),
        sa.Column("resolution", sa.Text, nullable=True),
        sa.Column("reported_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("assigned_to", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reported_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("contained_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trust_incident_org_status", "trust_incidents", ["org_id", "status"])
    op.create_index("ix_trust_incident_severity", "trust_incidents", ["severity"])
    op.create_index("ix_trust_incident_system", "trust_incidents", ["system_id"])

    # ── trust_incident_actions ───────────────────────────────────────
    op.create_table(
        "trust_incident_actions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("incident_id", sa.String(26), sa.ForeignKey("trust_incidents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action_type", trust_incident_action_type, nullable=False),
        sa.Column("status", trust_incident_action_status, nullable=False, server_default="pending"),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("target_type", sa.String(40), nullable=True),
        sa.Column("target_id", sa.String(26), nullable=True),
        sa.Column("performed_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("result", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_trust_inc_action_incident", "trust_incident_actions", ["incident_id"])
    op.create_index("ix_trust_inc_action_type", "trust_incident_actions", ["action_type"])


def downgrade() -> None:
    op.drop_table("trust_incident_actions")
    op.drop_table("trust_incidents")
    op.drop_table("trust_monitor_alerts")
    op.drop_table("trust_monitors")
    op.execute("DROP TYPE IF EXISTS trust_incident_action_status")
    op.execute("DROP TYPE IF EXISTS trust_incident_action_type")
    op.execute("DROP TYPE IF EXISTS trust_incident_status")
    op.execute("DROP TYPE IF EXISTS trust_incident_severity")
    op.execute("DROP TYPE IF EXISTS trust_alert_status")
    op.execute("DROP TYPE IF EXISTS trust_alert_severity")
    op.execute("DROP TYPE IF EXISTS trust_monitor_status")
    op.execute("DROP TYPE IF EXISTS trust_monitor_type")
