"""Developer Platform — extension SDK, sandboxed apps, connector marketplace.

Revision ID: devplatform01
Revises: talent15_performance_indexes
Create Date: 2026-10-22
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "devplatform01"
down_revision = "talent15a00015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Developer Accounts ───────────────────────────────
    op.create_table(
        "developer_accounts",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("owner_user_id", sa.String(26), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="SET NULL")),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(60), nullable=False),
        sa.Column("website_url", sa.String(500)),
        sa.Column("support_email", sa.String(255), nullable=False),
        sa.Column("verified", sa.Boolean, default=False),
        sa.Column("status", sa.Enum("ACTIVE", "SUSPENDED", "REVOKED", name="developer_status", create_constraint=True), default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_dev_accounts_slug", "developer_accounts", ["slug"], unique=True)
    op.create_index("ix_dev_accounts_owner", "developer_accounts", ["owner_user_id"])
    op.create_index("ix_dev_accounts_org", "developer_accounts", ["org_id"])

    # ── Developer Apps ───────────────────────────────────
    op.create_table(
        "developer_apps",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("developer_id", sa.String(26), sa.ForeignKey("developer_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(60), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("icon_url", sa.String(500)),
        sa.Column("homepage_url", sa.String(500)),
        sa.Column("privacy_policy_url", sa.String(500)),
        sa.Column("category", sa.Enum("CONNECTOR", "WORKFLOW_ADAPTER", "UI_EXTENSION", "ANALYTICS", "AUTOMATION", "CONTENT_PACK", "ECOSYSTEM_SOURCE", name="app_category", create_constraint=True), nullable=False),
        sa.Column("visibility", sa.Enum("PRIVATE", "UNLISTED", "PUBLIC", name="app_visibility", create_constraint=True), default="PRIVATE"),
        sa.Column("status", sa.Enum("DRAFT", "TESTING", "SUBMITTED", "APPROVED", "PUBLISHED", "DEPRECATED", "REVOKED", name="app_status", create_constraint=True), default="DRAFT"),
        sa.Column("manifest", postgresql.JSONB),
        sa.Column("oauth_client_id", sa.String(64)),
        sa.Column("oauth_client_secret_hash", sa.String(128)),
        sa.Column("redirect_uris", postgresql.JSONB, default=[]),
        sa.Column("webhook_url", sa.String(500)),
        sa.Column("webhook_secret_hash", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_dev_apps_dev_slug", "developer_apps", ["developer_id", "slug"], unique=True)
    op.create_index("ix_dev_apps_status", "developer_apps", ["status"])
    op.create_index("ix_dev_apps_category", "developer_apps", ["category"])
    op.create_index("ix_dev_apps_visibility", "developer_apps", ["visibility"])
    op.create_index("ix_dev_apps_oauth_client", "developer_apps", ["oauth_client_id"], unique=True)

    # ── App Versions ─────────────────────────────────────
    op.create_table(
        "app_versions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("app_id", sa.String(26), sa.ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("manifest", postgresql.JSONB, nullable=False),
        sa.Column("changelog", sa.Text),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("signature", sa.String(512)),
        sa.Column("review_status", sa.Enum("PENDING", "APPROVED", "REJECTED", "REVOKED", name="app_version_review_status", create_constraint=True), default="PENDING"),
        sa.Column("review_notes", sa.Text),
        sa.Column("reviewed_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("min_platform_version", sa.String(10)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_app_versions_app_ver", "app_versions", ["app_id", "version"], unique=True)
    op.create_index("ix_app_versions_review", "app_versions", ["review_status"])

    # ── App Installations ────────────────────────────────
    op.create_table(
        "app_installations",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("app_id", sa.String(26), sa.ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("app_version_id", sa.String(26), sa.ForeignKey("app_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("org_id", sa.String(26), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", sa.String(26)),
        sa.Column("installed_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "SUSPENDED", "UNINSTALLED", name="installation_status", create_constraint=True), default="ACTIVE"),
        sa.Column("granted_permissions", postgresql.JSONB, default=[]),
        sa.Column("config", postgresql.JSONB, default={}),
        sa.Column("pinned_version", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("uninstalled_at", sa.DateTime(timezone=True)),
    )
    op.create_index("uq_app_installs_app_org", "app_installations", ["app_id", "org_id"], unique=True, postgresql_where=sa.text("status = 'ACTIVE'"))
    op.create_index("ix_app_installs_org", "app_installations", ["org_id"])
    op.create_index("ix_app_installs_tenant", "app_installations", ["tenant_id"])

    # ── App API Keys ─────────────────────────────────────
    op.create_table(
        "app_api_keys",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("app_id", sa.String(26), sa.ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("installation_id", sa.String(26), sa.ForeignKey("app_installations.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("key_prefix", sa.String(12), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("scopes", postgresql.JSONB, default=[]),
        sa.Column("rate_limit_tier", sa.Enum("STANDARD", "ELEVATED", "UNLIMITED", name="rate_limit_tier", create_constraint=True), default="STANDARD"),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_app_api_keys_prefix", "app_api_keys", ["key_prefix"])
    op.create_index("ix_app_api_keys_hash", "app_api_keys", ["key_hash"], unique=True)
    op.create_index("ix_app_api_keys_app", "app_api_keys", ["app_id"])
    op.create_index("ix_app_api_keys_install", "app_api_keys", ["installation_id"])

    # ── App Event Subscriptions ──────────────────────────
    op.create_table(
        "app_event_subscriptions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("installation_id", sa.String(26), sa.ForeignKey("app_installations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("filter_expression", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_app_event_subs_event", "app_event_subscriptions", ["event_type"])
    op.create_index("ix_app_event_subs_install", "app_event_subscriptions", ["installation_id"])
    op.create_index("uq_app_event_subs_install_event", "app_event_subscriptions", ["installation_id", "event_type"], unique=True)

    # ── App Automation Rules ─────────────────────────────
    op.create_table(
        "app_automation_rules",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("installation_id", sa.String(26), sa.ForeignKey("app_installations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("trigger_event", sa.String(100), nullable=False),
        sa.Column("trigger_filter", postgresql.JSONB),
        sa.Column("action_type", sa.Enum("WEBHOOK", "SANDBOX_FUNCTION", "API_CALL", "NOTIFICATION", name="automation_action_type", create_constraint=True), nullable=False),
        sa.Column("action_config", postgresql.JSONB, nullable=False),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("max_executions_per_hour", sa.Integer, default=100),
        sa.Column("last_executed_at", sa.DateTime(timezone=True)),
        sa.Column("execution_count", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_app_auto_rules_install", "app_automation_rules", ["installation_id"])
    op.create_index("ix_app_auto_rules_event", "app_automation_rules", ["trigger_event"])

    # ── App Secrets ──────────────────────────────────────
    op.create_table(
        "app_secrets",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("installation_id", sa.String(26), sa.ForeignKey("app_installations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("encrypted_value", sa.Text, nullable=False),
        sa.Column("description", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("uq_app_secrets_install_key", "app_secrets", ["installation_id", "key"], unique=True)

    # ── App UI Extensions ────────────────────────────────
    op.create_table(
        "app_ui_extensions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("app_id", sa.String(26), sa.ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("surface", sa.Enum("DASHBOARD_CARD", "PROJECT_SIDEBAR", "COHORT_TOOL", "SUBMISSION_PANEL", "REGISTRY_DETAIL", "SETTINGS_PAGE", "CLIENT_PORTAL_WIDGET", "OPERATOR_CONSOLE", name="ui_surface", create_constraint=True), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("entry_path", sa.String(500), nullable=False),
        sa.Column("viewport_width", sa.Integer),
        sa.Column("viewport_height", sa.Integer),
        sa.Column("config_schema", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_app_ui_ext_app", "app_ui_extensions", ["app_id"])
    op.create_index("ix_app_ui_ext_surface", "app_ui_extensions", ["surface"])

    # ── Sandbox Executions ───────────────────────────────
    op.create_table(
        "sandbox_executions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("installation_id", sa.String(26), sa.ForeignKey("app_installations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("app_version_id", sa.String(26), sa.ForeignKey("app_versions.id", ondelete="SET NULL"), nullable=False),
        sa.Column("function_name", sa.String(200), nullable=False),
        sa.Column("trigger_type", sa.String(50), nullable=False),
        sa.Column("trigger_event", sa.String(100)),
        sa.Column("status", sa.Enum("RUNNING", "COMPLETED", "FAILED", "TIMEOUT", "CANCELLED", name="sandbox_execution_status", create_constraint=True), nullable=False),
        sa.Column("duration_ms", sa.Integer),
        sa.Column("memory_peak_mb", sa.Float),
        sa.Column("input_payload", postgresql.JSONB),
        sa.Column("output_payload", postgresql.JSONB),
        sa.Column("error_message", sa.Text),
        sa.Column("logs", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_sandbox_exec_install", "sandbox_executions", ["installation_id", "created_at"])
    op.create_index("ix_sandbox_exec_status", "sandbox_executions", ["status"])

    # ── App Review Submissions ───────────────────────────
    op.create_table(
        "app_review_submissions",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("app_id", sa.String(26), sa.ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("app_version_id", sa.String(26), sa.ForeignKey("app_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("submitted_by", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("review_status", sa.Enum("PENDING", "APPROVED", "REJECTED", "REVOKED", name="app_version_review_status", create_constraint=True, create_type=False), default="PENDING"),
        sa.Column("reviewer_id", sa.String(26), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("review_notes", sa.Text),
        sa.Column("automated_checks", postgresql.JSONB),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_app_review_app", "app_review_submissions", ["app_id"])
    op.create_index("ix_app_review_status", "app_review_submissions", ["review_status"])

    # ── App Signing Keys ─────────────────────────────────
    op.create_table(
        "app_signing_keys",
        sa.Column("id", sa.String(26), primary_key=True),
        sa.Column("developer_id", sa.String(26), sa.ForeignKey("developer_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("public_key", sa.Text, nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_primary", sa.Boolean, default=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_app_signing_keys_dev", "app_signing_keys", ["developer_id"])


def downgrade() -> None:
    op.drop_table("app_signing_keys")
    op.drop_table("app_review_submissions")
    op.drop_table("sandbox_executions")
    op.drop_table("app_ui_extensions")
    op.drop_table("app_secrets")
    op.drop_table("app_automation_rules")
    op.drop_table("app_event_subscriptions")
    op.drop_table("app_api_keys")
    op.drop_table("app_installations")
    op.drop_table("app_versions")
    op.drop_table("developer_apps")
    op.drop_table("developer_accounts")

    # Drop enum types
    for enum_name in [
        "developer_status", "app_category", "app_visibility", "app_status",
        "app_version_review_status", "installation_status", "rate_limit_tier",
        "automation_action_type", "sandbox_execution_status", "ui_surface",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
