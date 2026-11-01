"""ops01: Global Operations & Governance Plane (Issue #46).

Creates all operations plane tables covering infrastructure,
reliability, and governance across Parts A–S.

Revision ID: ops01a00001
Revises: trust06a00006
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "ops01a00001"
down_revision: str = "trust06a00006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Infrastructure enums ─────────────────────────────────────────
    op.execute("CREATE TYPE ops_region_status AS ENUM ('active', 'draining', 'standby', 'disabled')")
    op.execute("CREATE TYPE ops_cell_status AS ENUM ('healthy', 'degraded', 'unhealthy', 'draining', 'offline')")
    op.execute("CREATE TYPE ops_service_status AS ENUM ('running', 'degraded', 'stopped', 'deploying', 'failed')")

    # ── Reliability enums ────────────────────────────────────────────
    op.execute("CREATE TYPE ops_slo_status AS ENUM ('met', 'at_risk', 'breached', 'paused')")
    op.execute("CREATE TYPE ops_incident_severity AS ENUM ('sev1', 'sev2', 'sev3', 'sev4')")
    op.execute("CREATE TYPE ops_incident_status AS ENUM ('detected', 'acknowledged', 'investigating', 'mitigating', 'resolved', 'post_mortem', 'closed')")
    op.execute("CREATE TYPE ops_detection_rule_status AS ENUM ('active', 'disabled', 'testing')")
    op.execute("CREATE TYPE ops_failover_status AS ENUM ('idle', 'triggered', 'in_progress', 'completed', 'rolled_back', 'failed')")
    op.execute("CREATE TYPE ops_recovery_plan_status AS ENUM ('draft', 'active', 'tested', 'deprecated')")

    # ── Governance enums ─────────────────────────────────────────────
    op.execute("CREATE TYPE ops_policy_status AS ENUM ('draft', 'active', 'disabled', 'deprecated')")
    op.execute("CREATE TYPE ops_playbook_status AS ENUM ('draft', 'approved', 'active', 'deprecated')")
    op.execute("CREATE TYPE ops_playbook_run_status AS ENUM ('pending_approval', 'approved', 'running', 'completed', 'failed', 'rolled_back', 'cancelled')")
    op.execute("CREATE TYPE ops_cost_category AS ENUM ('compute', 'ai_inference', 'storage', 'network', 'database', 'third_party', 'licensing')")
    op.execute("CREATE TYPE ops_game_day_status AS ENUM ('planned', 'running', 'completed', 'cancelled')")
    op.execute("CREATE TYPE ops_healing_action_status AS ENUM ('proposed', 'approved', 'executing', 'completed', 'rejected', 'failed')")

    # ── Infrastructure tables ────────────────────────────────────────
    op.create_table("ops_deployment_regions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("status", sa.Enum("active", "draining", "standby", "disabled", name="ops_region_status", create_constraint=False), nullable=False, server_default="active"),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_ops_region_code", "ops_deployment_regions", ["code"], unique=True)

    op.create_table("ops_runtime_cells",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("region_id", sa.String(26), sa.ForeignKey("ops_deployment_regions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("status", sa.Enum("healthy", "degraded", "unhealthy", "draining", "offline", name="ops_cell_status", create_constraint=False), nullable=False, server_default="healthy"),
        sa.Column("capacity", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("current_load", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("tenant_ids", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_cell_region", "ops_runtime_cells", ["region_id"])
    op.create_index("ix_ops_cell_status", "ops_runtime_cells", ["status"])

    op.create_table("ops_service_instances",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("cell_id", sa.String(26), sa.ForeignKey("ops_runtime_cells.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_name", sa.String(100), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("status", sa.Enum("running", "degraded", "stopped", "deploying", "failed", name="ops_service_status", create_constraint=False), nullable=False, server_default="running"),
        sa.Column("endpoint", sa.String(500), nullable=True),
        sa.Column("health_check_url", sa.String(500), nullable=True),
        sa.Column("metrics", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_service_cell", "ops_service_instances", ["cell_id"])
    op.create_index("ix_ops_service_name", "ops_service_instances", ["service_name"])

    op.create_table("ops_routing_rules",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("tenant_id", sa.String(26), nullable=True),
        sa.Column("source_region_id", sa.String(26), nullable=True),
        sa.Column("target_region_id", sa.String(26), sa.ForeignKey("ops_deployment_regions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conditions", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("weight", sa.Integer, nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_routing_tenant", "ops_routing_rules", ["tenant_id"])

    op.create_table("ops_metric_samples",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("source_type", sa.String(40), nullable=False),
        sa.Column("source_id", sa.String(26), nullable=False),
        sa.Column("value", sa.Numeric(12, 4), nullable=False),
        sa.Column("labels", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("sampled_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_metric_name_time", "ops_metric_samples", ["metric_name", "sampled_at"])
    op.create_index("ix_ops_metric_source", "ops_metric_samples", ["source_type", "source_id"])

    # ── Reliability tables ───────────────────────────────────────────
    op.create_table("ops_slo_definitions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("org_id", sa.String(26), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("sli_metric", sa.String(100), nullable=False),
        sa.Column("target_value", sa.Numeric(10, 4), nullable=False),
        sa.Column("target_unit", sa.String(20), nullable=False),
        sa.Column("window_days", sa.Integer, nullable=False, server_default="30"),
        sa.Column("error_budget_total", sa.Numeric(10, 4), nullable=False),
        sa.Column("error_budget_remaining", sa.Numeric(10, 4), nullable=False),
        sa.Column("status", sa.Enum("met", "at_risk", "breached", "paused", name="ops_slo_status", create_constraint=False), nullable=False, server_default="met"),
        sa.Column("alert_thresholds", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_slo_org", "ops_slo_definitions", ["org_id"])
    op.create_index("ix_ops_slo_status", "ops_slo_definitions", ["status"])

    op.create_table("ops_incidents",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("severity", sa.Enum("sev1", "sev2", "sev3", "sev4", name="ops_incident_severity", create_constraint=False), nullable=False),
        sa.Column("status", sa.Enum("detected", "acknowledged", "investigating", "mitigating", "resolved", "post_mortem", "closed", name="ops_incident_status", create_constraint=False), nullable=False, server_default="detected"),
        sa.Column("region_id", sa.String(26), nullable=True),
        sa.Column("affected_services", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("affected_tenants", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("detection_source", sa.String(40), nullable=False, server_default="manual"),
        sa.Column("root_cause", sa.Text, nullable=True),
        sa.Column("timeline", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("slo_impact", postgresql.JSONB, nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_incident_severity", "ops_incidents", ["severity"])
    op.create_index("ix_ops_incident_status", "ops_incidents", ["status"])
    op.create_index("ix_ops_incident_region", "ops_incidents", ["region_id"])

    op.create_table("ops_detection_rules",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("rule_type", sa.String(40), nullable=False),
        sa.Column("conditions", postgresql.JSONB, nullable=False),
        sa.Column("severity", sa.Enum("sev1", "sev2", "sev3", "sev4", name="ops_incident_severity", create_constraint=False), nullable=False),
        sa.Column("status", sa.Enum("active", "disabled", "testing", name="ops_detection_rule_status", create_constraint=False), nullable=False, server_default="active"),
        sa.Column("cooldown_minutes", sa.Integer, nullable=False, server_default="15"),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_detection_status", "ops_detection_rules", ["status"])

    op.create_table("ops_failover_records",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("source_region_id", sa.String(26), nullable=False),
        sa.Column("target_region_id", sa.String(26), nullable=False),
        sa.Column("trigger", sa.String(40), nullable=False),
        sa.Column("incident_id", sa.String(26), nullable=True),
        sa.Column("status", sa.Enum("idle", "triggered", "in_progress", "completed", "rolled_back", "failed", name="ops_failover_status", create_constraint=False), nullable=False, server_default="triggered"),
        sa.Column("services_migrated", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("tenants_migrated", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("initiated_by", sa.String(26), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_failover_status", "ops_failover_records", ["status"])
    op.create_index("ix_ops_failover_created", "ops_failover_records", ["created_at"])

    op.create_table("ops_recovery_plans",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("scenario", sa.String(100), nullable=False),
        sa.Column("status", sa.Enum("draft", "active", "tested", "deprecated", name="ops_recovery_plan_status", create_constraint=False), nullable=False, server_default="draft"),
        sa.Column("steps", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("rto_minutes", sa.Integer, nullable=True),
        sa.Column("rpo_minutes", sa.Integer, nullable=True),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("test_results", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_recovery_status", "ops_recovery_plans", ["status"])

    # ── Governance tables ────────────────────────────────────────────
    op.create_table("ops_policies",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("policy_type", sa.String(40), nullable=False),
        sa.Column("status", sa.Enum("draft", "active", "disabled", "deprecated", name="ops_policy_status", create_constraint=False), nullable=False, server_default="draft"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("rules", postgresql.JSONB, nullable=False),
        sa.Column("enforcement_mode", sa.String(20), nullable=False, server_default="enforce"),
        sa.Column("scope", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_policy_type", "ops_policies", ["policy_type"])
    op.create_index("ix_ops_policy_status", "ops_policies", ["status"])

    op.create_table("ops_remediation_playbooks",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("trigger_conditions", postgresql.JSONB, nullable=False),
        sa.Column("steps", postgresql.JSONB, nullable=False),
        sa.Column("rollback_steps", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("requires_approval", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("blast_radius_check", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("status", sa.Enum("draft", "approved", "active", "deprecated", name="ops_playbook_status", create_constraint=False), nullable=False, server_default="draft"),
        sa.Column("max_concurrent", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_playbook_status", "ops_remediation_playbooks", ["status"])

    op.create_table("ops_playbook_runs",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("playbook_id", sa.String(26), sa.ForeignKey("ops_remediation_playbooks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("incident_id", sa.String(26), nullable=True),
        sa.Column("status", sa.Enum("pending_approval", "approved", "running", "completed", "failed", "rolled_back", "cancelled", name="ops_playbook_run_status", create_constraint=False), nullable=False, server_default="pending_approval"),
        sa.Column("step_results", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("approved_by", sa.String(26), nullable=True),
        sa.Column("executed_by", sa.String(26), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_pbrun_playbook", "ops_playbook_runs", ["playbook_id"])
    op.create_index("ix_ops_pbrun_status", "ops_playbook_runs", ["status"])

    op.create_table("ops_cost_records",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("tenant_id", sa.String(26), nullable=True),
        sa.Column("category", sa.Enum("compute", "ai_inference", "storage", "network", "database", "third_party", "licensing", name="ops_cost_category", create_constraint=False), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("service_name", sa.String(100), nullable=False),
        sa.Column("region_id", sa.String(26), nullable=True),
        sa.Column("amount_minor", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_cost_category", "ops_cost_records", ["category"])
    op.create_index("ix_ops_cost_period", "ops_cost_records", ["period_start", "period_end"])
    op.create_index("ix_ops_cost_tenant", "ops_cost_records", ["tenant_id"])

    op.create_table("ops_cost_budgets",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("tenant_id", sa.String(26), nullable=True),
        sa.Column("category", sa.String(40), nullable=True),
        sa.Column("budget_minor", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("period", sa.String(20), nullable=False, server_default="monthly"),
        sa.Column("current_spend_minor", sa.Integer, nullable=False, server_default="0"),
        sa.Column("alert_thresholds", postgresql.JSONB, nullable=False, server_default="[50, 80, 100]"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_budget_tenant", "ops_cost_budgets", ["tenant_id"])

    op.create_table("ops_capacity_forecasts",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("region_id", sa.String(26), nullable=True),
        sa.Column("resource_type", sa.String(40), nullable=False),
        sa.Column("current_usage", sa.Numeric(12, 4), nullable=False),
        sa.Column("projected_usage", sa.Numeric(12, 4), nullable=False),
        sa.Column("capacity_limit", sa.Numeric(12, 4), nullable=False),
        sa.Column("forecast_horizon_days", sa.Integer, nullable=False, server_default="30"),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=False),
        sa.Column("recommendations", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_capacity_region", "ops_capacity_forecasts", ["region_id"])

    op.create_table("ops_compliance_evidence",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("framework", sa.String(60), nullable=False),
        sa.Column("control_id", sa.String(60), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="collected"),
        sa.Column("evidence_data", postgresql.JSONB, nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_compliance_framework", "ops_compliance_evidence", ["framework"])

    op.create_table("ops_retention_policies",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("data_category", sa.String(60), nullable=False),
        sa.Column("retention_days", sa.Integer, nullable=False),
        sa.Column("deletion_strategy", sa.String(40), nullable=False, server_default="soft_delete"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table("ops_change_records",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("change_type", sa.String(40), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="low"),
        sa.Column("status", sa.String(20), nullable=False, server_default="proposed"),
        sa.Column("affected_services", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("rollback_plan", sa.Text, nullable=True),
        sa.Column("approved_by", sa.String(26), nullable=True),
        sa.Column("executed_by", sa.String(26), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_change_status", "ops_change_records", ["status"])
    op.create_index("ix_ops_change_created", "ops_change_records", ["created_at"])

    op.create_table("ops_governance_approvals",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("target_type", sa.String(40), nullable=False),
        sa.Column("target_id", sa.String(26), nullable=False),
        sa.Column("approval_type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("requested_by", sa.String(26), nullable=False),
        sa.Column("decided_by", sa.String(26), nullable=True),
        sa.Column("rationale", sa.Text, nullable=True),
        sa.Column("conditions", sa.Text, nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_approval_target", "ops_governance_approvals", ["target_type", "target_id"])
    op.create_index("ix_ops_approval_status", "ops_governance_approvals", ["status"])

    op.create_table("ops_game_days",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("scenario", sa.String(100), nullable=False),
        sa.Column("status", sa.Enum("planned", "running", "completed", "cancelled", name="ops_game_day_status", create_constraint=False), nullable=False, server_default="planned"),
        sa.Column("plan", postgresql.JSONB, nullable=False),
        sa.Column("results", postgresql.JSONB, nullable=True),
        sa.Column("participants", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("lessons_learned", sa.Text, nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(26), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table("ops_healing_actions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("incident_id", sa.String(26), nullable=True),
        sa.Column("detection_rule_id", sa.String(26), nullable=True),
        sa.Column("playbook_id", sa.String(26), nullable=True),
        sa.Column("action_type", sa.String(40), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", sa.Enum("proposed", "approved", "executing", "completed", "rejected", "failed", name="ops_healing_action_status", create_constraint=False), nullable=False, server_default="proposed"),
        sa.Column("blast_radius", postgresql.JSONB, nullable=True),
        sa.Column("requires_human_approval", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("approved_by", sa.String(26), nullable=True),
        sa.Column("result", postgresql.JSONB, nullable=True),
        sa.Column("proposed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_ops_healing_status", "ops_healing_actions", ["status"])
    op.create_index("ix_ops_healing_incident", "ops_healing_actions", ["incident_id"])


def downgrade() -> None:
    for table in [
        "ops_healing_actions", "ops_game_days", "ops_governance_approvals",
        "ops_change_records", "ops_retention_policies", "ops_compliance_evidence",
        "ops_capacity_forecasts", "ops_cost_budgets", "ops_cost_records",
        "ops_playbook_runs", "ops_remediation_playbooks", "ops_policies",
        "ops_recovery_plans", "ops_failover_records", "ops_detection_rules",
        "ops_incidents", "ops_slo_definitions", "ops_metric_samples",
        "ops_routing_rules", "ops_service_instances", "ops_runtime_cells",
        "ops_deployment_regions",
    ]:
        op.drop_table(table)
    for enum_name in [
        "ops_healing_action_status", "ops_game_day_status", "ops_cost_category",
        "ops_playbook_run_status", "ops_playbook_status", "ops_policy_status",
        "ops_recovery_plan_status", "ops_failover_status", "ops_detection_rule_status",
        "ops_incident_status", "ops_incident_severity", "ops_slo_status",
        "ops_service_status", "ops_cell_status", "ops_region_status",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
