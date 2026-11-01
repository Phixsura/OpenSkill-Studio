"""Developer Platform models — third-party extension ecosystem.

Entities: DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, ulid_pk

# ── Enums ────────────────────────────────────────────────


class DeveloperStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class AppCategory(str, enum.Enum):
    CONNECTOR = "connector"
    WORKFLOW_ADAPTER = "workflow_adapter"
    UI_EXTENSION = "ui_extension"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"
    CONTENT_PACK = "content_pack"
    ECOSYSTEM_SOURCE = "ecosystem_source"


class AppVisibility(str, enum.Enum):
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"


class AppStatus(str, enum.Enum):
    DRAFT = "draft"
    TESTING = "testing"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"


class AppVersionReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"


class InstallationStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    UNINSTALLED = "uninstalled"


class RateLimitTier(str, enum.Enum):
    STANDARD = "standard"
    ELEVATED = "elevated"
    UNLIMITED = "unlimited"


class AutomationActionType(str, enum.Enum):
    WEBHOOK = "webhook"
    SANDBOX_FUNCTION = "sandbox_function"
    API_CALL = "api_call"
    NOTIFICATION = "notification"


class SandboxExecutionStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class UiSurface(str, enum.Enum):
    DASHBOARD_CARD = "dashboard_card"
    PROJECT_SIDEBAR = "project_sidebar"
    COHORT_TOOL = "cohort_tool"
    SUBMISSION_PANEL = "submission_panel"
    REGISTRY_DETAIL = "registry_detail"
    SETTINGS_PAGE = "settings_page"
    CLIENT_PORTAL_WIDGET = "client_portal_widget"
    OPERATOR_CONSOLE = "operator_console"


# ── Developer Account ────────────────────────────────────


class DeveloperAccount(Base):
    __tablename__ = "developer_accounts"
    __table_args__ = (
        Index("uq_dev_accounts_slug", "slug", unique=True),
        Index("ix_dev_accounts_owner", "owner_user_id"),
        Index("ix_dev_accounts_org", "org_id"),
    )

    id: Mapped[str] = ulid_pk()
    owner_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="SET NULL")
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(60), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(500))
    support_email: Mapped[str] = mapped_column(String(255), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[DeveloperStatus] = mapped_column(
        Enum(DeveloperStatus, name="developer_status", create_constraint=True),
        default=DeveloperStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    apps: Mapped[list["DeveloperApp"]] = relationship(back_populates="developer")


# ── Developer App ────────────────────────────────────────


class DeveloperApp(Base):
    __tablename__ = "developer_apps"
    __table_args__ = (
        Index("uq_dev_apps_dev_slug", "developer_id", "slug", unique=True),
        Index("ix_dev_apps_status", "status"),
        Index("ix_dev_apps_category", "category"),
        Index("ix_dev_apps_visibility", "visibility"),
        Index("ix_dev_apps_oauth_client", "oauth_client_id", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    developer_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("developer_accounts.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon_url: Mapped[str | None] = mapped_column(String(500))
    homepage_url: Mapped[str | None] = mapped_column(String(500))
    privacy_policy_url: Mapped[str | None] = mapped_column(String(500))
    category: Mapped[AppCategory] = mapped_column(
        Enum(AppCategory, name="app_category", create_constraint=True),
        nullable=False,
    )
    visibility: Mapped[AppVisibility] = mapped_column(
        Enum(AppVisibility, name="app_visibility", create_constraint=True),
        default=AppVisibility.PRIVATE,
    )
    status: Mapped[AppStatus] = mapped_column(
        Enum(AppStatus, name="app_status", create_constraint=True),
        default=AppStatus.DRAFT,
    )
    manifest: Mapped[dict | None] = mapped_column(JSONB)
    oauth_client_id: Mapped[str | None] = mapped_column(String(64))
    oauth_client_secret_hash: Mapped[str | None] = mapped_column(String(128))
    redirect_uris: Mapped[list | None] = mapped_column(JSONB, default=list)
    webhook_url: Mapped[str | None] = mapped_column(String(500))
    webhook_secret_hash: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    developer: Mapped["DeveloperAccount"] = relationship(back_populates="apps")
    versions: Mapped[list["AppVersion"]] = relationship(back_populates="app")
    installations: Mapped[list["AppInstallation"]] = relationship(back_populates="app")
    api_keys: Mapped[list["AppApiKey"]] = relationship(back_populates="app")


# ── App Version ──────────────────────────────────────────


class AppVersion(Base):
    __tablename__ = "app_versions"
    __table_args__ = (
        Index("uq_app_versions_app_ver", "app_id", "version", unique=True),
        Index("ix_app_versions_review", "review_status"),
    )

    id: Mapped[str] = ulid_pk()
    app_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    manifest: Mapped[dict] = mapped_column(JSONB, nullable=False)
    changelog: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    signature: Mapped[str | None] = mapped_column(String(512))
    review_status: Mapped[AppVersionReviewStatus] = mapped_column(
        Enum(AppVersionReviewStatus, name="app_version_review_status", create_constraint=True),
        default=AppVersionReviewStatus.PENDING,
    )
    review_notes: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL")
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    min_platform_version: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    app: Mapped["DeveloperApp"] = relationship(back_populates="versions")


# ── App Installation ─────────────────────────────────────


class AppInstallation(Base):
    __tablename__ = "app_installations"
    __table_args__ = (
        Index(
            "uq_app_installs_app_org",
            "app_id",
            "org_id",
            unique=True,
            postgresql_where="status = 'active'",
        ),
        Index("ix_app_installs_org", "org_id"),
        Index("ix_app_installs_tenant", "tenant_id"),
    )

    id: Mapped[str] = ulid_pk()
    app_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False
    )
    app_version_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("app_versions.id", ondelete="RESTRICT"), nullable=False
    )
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[str | None] = mapped_column(String(26))
    installed_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    status: Mapped[InstallationStatus] = mapped_column(
        Enum(InstallationStatus, name="installation_status", create_constraint=True),
        default=InstallationStatus.ACTIVE,
    )
    granted_permissions: Mapped[list] = mapped_column(JSONB, default=list)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    pinned_version: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    uninstalled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    app: Mapped["DeveloperApp"] = relationship(back_populates="installations")
    version: Mapped["AppVersion"] = relationship()
    secrets: Mapped[list["AppSecret"]] = relationship(back_populates="installation")
    event_subscriptions: Mapped[list["AppEventSubscription"]] = relationship(
        back_populates="installation"
    )


# ── App API Key ──────────────────────────────────────────


class AppApiKey(Base):
    __tablename__ = "app_api_keys"
    __table_args__ = (
        Index("ix_app_api_keys_prefix", "key_prefix"),
        Index("ix_app_api_keys_hash", "key_hash", unique=True),
        Index("ix_app_api_keys_app", "app_id"),
        Index("ix_app_api_keys_install", "installation_id"),
    )

    id: Mapped[str] = ulid_pk()
    app_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False
    )
    installation_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("app_installations.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    scopes: Mapped[list] = mapped_column(JSONB, default=list)
    rate_limit_tier: Mapped[RateLimitTier] = mapped_column(
        Enum(RateLimitTier, name="rate_limit_tier", create_constraint=True),
        default=RateLimitTier.STANDARD,
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    app: Mapped["DeveloperApp"] = relationship(back_populates="api_keys")


# ── App Event Subscription ───────────────────────────────


class AppEventSubscription(Base):
    __tablename__ = "app_event_subscriptions"
    __table_args__ = (
        Index("ix_app_event_subs_event", "event_type"),
        Index("ix_app_event_subs_install", "installation_id"),
        Index(
            "uq_app_event_subs_install_event",
            "installation_id",
            "event_type",
            unique=True,
        ),
    )

    id: Mapped[str] = ulid_pk()
    installation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("app_installations.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    filter_expression: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    installation: Mapped["AppInstallation"] = relationship(
        back_populates="event_subscriptions"
    )


# ── App Automation Rule ──────────────────────────────────


class AppAutomationRule(Base):
    __tablename__ = "app_automation_rules"
    __table_args__ = (
        Index("ix_app_auto_rules_install", "installation_id"),
        Index("ix_app_auto_rules_event", "trigger_event"),
    )

    id: Mapped[str] = ulid_pk()
    installation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("app_installations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    trigger_event: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger_filter: Mapped[dict | None] = mapped_column(JSONB)
    action_type: Mapped[AutomationActionType] = mapped_column(
        Enum(AutomationActionType, name="automation_action_type", create_constraint=True),
        nullable=False,
    )
    action_config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    max_executions_per_hour: Mapped[int] = mapped_column(Integer, default=100)
    last_executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── App Secret ───────────────────────────────────────────


class AppSecret(Base):
    __tablename__ = "app_secrets"
    __table_args__ = (
        Index("uq_app_secrets_install_key", "installation_id", "key", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    installation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("app_installations.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    installation: Mapped["AppInstallation"] = relationship(back_populates="secrets")


# ── App UI Extension ─────────────────────────────────────


class AppUiExtension(Base):
    __tablename__ = "app_ui_extensions"
    __table_args__ = (
        Index("ix_app_ui_ext_app", "app_id"),
        Index("ix_app_ui_ext_surface", "surface"),
    )

    id: Mapped[str] = ulid_pk()
    app_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False
    )
    surface: Mapped[UiSurface] = mapped_column(
        Enum(UiSurface, name="ui_surface", create_constraint=True),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    entry_path: Mapped[str] = mapped_column(String(500), nullable=False)
    viewport_width: Mapped[int | None] = mapped_column(Integer)
    viewport_height: Mapped[int | None] = mapped_column(Integer)
    config_schema: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ── Sandbox Execution Log ────────────────────────────────


class SandboxExecution(Base):
    __tablename__ = "sandbox_executions"
    __table_args__ = (
        Index("ix_sandbox_exec_install", "installation_id", "created_at"),
        Index("ix_sandbox_exec_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    installation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("app_installations.id", ondelete="CASCADE"), nullable=False
    )
    app_version_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("app_versions.id", ondelete="SET NULL"), nullable=False
    )
    function_name: Mapped[str] = mapped_column(String(200), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_event: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[SandboxExecutionStatus] = mapped_column(
        Enum(SandboxExecutionStatus, name="sandbox_execution_status", create_constraint=True),
        nullable=False,
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    memory_peak_mb: Mapped[float | None] = mapped_column(Float)
    input_payload: Mapped[dict | None] = mapped_column(JSONB)
    output_payload: Mapped[dict | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)
    logs: Mapped[list | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ── App Review Submission ─────────────────────────────────


class AppReviewSubmission(Base):
    __tablename__ = "app_review_submissions"
    __table_args__ = (
        Index("ix_app_review_app", "app_id"),
        Index("ix_app_review_status", "review_status"),
    )

    id: Mapped[str] = ulid_pk()
    app_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False
    )
    app_version_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("app_versions.id", ondelete="CASCADE"), nullable=False
    )
    submitted_by: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    review_status: Mapped[AppVersionReviewStatus] = mapped_column(
        Enum(
            AppVersionReviewStatus,
            name="app_version_review_status",
            create_constraint=True,
            create_type=False,
        ),
        default=AppVersionReviewStatus.PENDING,
    )
    reviewer_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL")
    )
    review_notes: Mapped[str | None] = mapped_column(Text)
    automated_checks: Mapped[dict | None] = mapped_column(JSONB)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ── App Signing Key ──────────────────────────────────────


class AppSigningKey(Base):
    __tablename__ = "app_signing_keys"
    __table_args__ = (
        Index("ix_app_signing_keys_dev", "developer_id"),
    )

    id: Mapped[str] = ulid_pk()
    developer_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("developer_accounts.id", ondelete="CASCADE"), nullable=False
    )
    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
