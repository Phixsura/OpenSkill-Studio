"""Pydantic schemas for the Developer Platform."""

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.base import reject_ctrl_json, reject_deep_json

# ── Developer Account ────────────────────────────────────


class CreateDeveloperAccountRequest(BaseModel):
    display_name: str
    slug: str
    website_url: str | None = None
    support_email: str
    org_id: str | None = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Display name must be 2-100 characters")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        import re

        v = v.strip().lower()
        if not re.match(r"^[a-z0-9][a-z0-9-]{0,58}[a-z0-9]$", v):
            raise ValueError(
                "Slug must be 2-60 chars, lowercase alphanumeric and hyphens, "
                "start/end with alphanumeric"
            )
        return v

    @field_validator("support_email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or len(v) > 255:
            raise ValueError("Invalid email address")
        return v


class UpdateDeveloperAccountRequest(BaseModel):
    display_name: str | None = None
    website_url: str | None = None
    support_email: str | None = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 100:
                raise ValueError("Display name must be 2-100 characters")
        return v


class DeveloperAccountResponse(BaseModel):
    id: str
    owner_user_id: str
    org_id: str | None
    display_name: str
    slug: str
    website_url: str | None
    support_email: str
    verified: bool
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Developer App ────────────────────────────────────────

VALID_APP_CATEGORIES = {
    "connector",
    "workflow_adapter",
    "ui_extension",
    "analytics",
    "automation",
    "content_pack",
    "ecosystem_source",
}

VALID_APP_VISIBILITIES = {"private", "unlisted", "public"}


class CreateAppRequest(BaseModel):
    name: str
    slug: str
    description: str | None = None
    category: str
    visibility: str = "private"
    icon_url: str | None = None
    homepage_url: str | None = None
    privacy_policy_url: str | None = None
    redirect_uris: list[str] = []
    webhook_url: str | None = None
    manifest: dict | None = None
    config_schema: dict | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Name must be 2-100 characters")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        import re

        v = v.strip().lower()
        if not re.match(r"^[a-z0-9][a-z0-9-]{0,58}[a-z0-9]$", v):
            raise ValueError(
                "Slug must be 2-60 chars, lowercase alphanumeric and hyphens"
            )
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in VALID_APP_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(sorted(VALID_APP_CATEGORIES))}")
        return v

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str) -> str:
        if v not in VALID_APP_VISIBILITIES:
            raise ValueError(
                f"Visibility must be one of: {', '.join(sorted(VALID_APP_VISIBILITIES))}"
            )
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 10000:
            raise ValueError("Description must be 10000 characters or less")
        return v

    @field_validator("redirect_uris")
    @classmethod
    def validate_redirect_uris(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("Maximum 10 redirect URIs allowed")
        for uri in v:
            if not uri.startswith("https://") and not uri.startswith("http://localhost"):
                raise ValueError(
                    f"Redirect URI must use HTTPS (or http://localhost for dev): {uri}"
                )
        return v

    @field_validator("manifest")
    @classmethod
    def validate_manifest(cls, v: dict | None) -> dict | None:
        if v is not None:
            reject_deep_json(v, "manifest")
            reject_ctrl_json(v, "manifest")
        return v


class UpdateAppRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    icon_url: str | None = None
    homepage_url: str | None = None
    privacy_policy_url: str | None = None
    visibility: str | None = None
    redirect_uris: list[str] | None = None
    webhook_url: str | None = None
    manifest: dict | None = None

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_APP_VISIBILITIES:
            raise ValueError(
                f"Visibility must be one of: {', '.join(sorted(VALID_APP_VISIBILITIES))}"
            )
        return v

    @field_validator("manifest")
    @classmethod
    def validate_manifest(cls, v: dict | None) -> dict | None:
        if v is not None:
            reject_deep_json(v, "manifest")
            reject_ctrl_json(v, "manifest")
        return v


class AppResponse(BaseModel):
    id: str
    developer_id: str
    name: str
    slug: str
    description: str | None
    icon_url: str | None
    homepage_url: str | None
    privacy_policy_url: str | None
    category: str
    visibility: str
    status: str
    manifest: dict | None
    oauth_client_id: str | None
    redirect_uris: list | None
    webhook_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppSummaryResponse(BaseModel):
    """Compact response for listings."""

    id: str
    name: str
    slug: str
    description: str | None
    icon_url: str | None
    category: str
    visibility: str
    status: str
    developer_name: str | None = None
    install_count: int = 0

    model_config = {"from_attributes": True}


# ── App Version ──────────────────────────────────────────


class CreateAppVersionRequest(BaseModel):
    version: str
    changelog: str | None = None
    manifest: dict
    content_hash: str
    signature: str | None = None
    min_platform_version: str | None = None

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        import re

        v = v.strip()
        if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$", v):
            raise ValueError("Version must follow semver (e.g. 1.0.0, 1.2.3-beta.1)")
        return v

    @field_validator("content_hash")
    @classmethod
    def validate_hash(cls, v: str) -> str:
        import re

        v = v.strip().lower()
        if not re.match(r"^[a-f0-9]{64}$", v):
            raise ValueError("content_hash must be a 64-char hex SHA-256")
        return v

    @field_validator("manifest")
    @classmethod
    def validate_manifest(cls, v: dict) -> dict:
        reject_deep_json(v, "manifest")
        reject_ctrl_json(v, "manifest")
        return v


class AppVersionResponse(BaseModel):
    id: str
    app_id: str
    version: str
    changelog: str | None
    content_hash: str
    signature: str | None
    review_status: str
    review_notes: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    min_platform_version: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── App Installation ─────────────────────────────────────


class InstallAppRequest(BaseModel):
    app_id: str
    app_version_id: str | None = None
    granted_permissions: list[str] = []
    config: dict = {}
    pinned_version: bool = False

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict) -> dict:
        reject_deep_json(v, "manifest")
        reject_ctrl_json(v, "manifest")
        return v


class UpdateInstallationRequest(BaseModel):
    config: dict | None = None
    pinned_version: bool | None = None
    granted_permissions: list[str] | None = None

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict | None) -> dict | None:
        if v is not None:
            reject_deep_json(v, "manifest")
            reject_ctrl_json(v, "manifest")
        return v


class AppInstallationResponse(BaseModel):
    id: str
    app_id: str
    app_version_id: str
    org_id: str
    tenant_id: str | None
    installed_by: str
    status: str
    granted_permissions: list
    config: dict
    pinned_version: bool
    created_at: datetime
    updated_at: datetime
    uninstalled_at: datetime | None

    model_config = {"from_attributes": True}


# ── App API Key ──────────────────────────────────────────


class CreateApiKeyRequest(BaseModel):
    name: str
    scopes: list[str] = []
    installation_id: str | None = None
    expires_in_days: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 100:
            raise ValueError("Name must be 1-100 characters")
        return v

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, v: list[str]) -> list[str]:
        if len(v) > 50:
            raise ValueError("Maximum 50 scopes allowed")
        return v


class ApiKeyResponse(BaseModel):
    id: str
    app_id: str
    installation_id: str | None
    name: str
    key_prefix: str
    scopes: list
    rate_limit_tier: str
    last_used_at: datetime | None
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreatedResponse(BaseModel):
    """Returned only on creation — contains the full key (shown once)."""

    id: str
    key: str
    key_prefix: str
    name: str
    scopes: list
    expires_at: datetime | None


# ── Event Subscription ───────────────────────────────────


class CreateEventSubscriptionRequest(BaseModel):
    event_type: str
    filter_expression: dict | None = None

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 100:
            raise ValueError("event_type must be 1-100 characters")
        return v


class EventSubscriptionResponse(BaseModel):
    id: str
    installation_id: str
    event_type: str
    enabled: bool
    filter_expression: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Automation Rule ──────────────────────────────────────

VALID_ACTION_TYPES = {"webhook", "sandbox_function", "api_call", "notification"}


class CreateAutomationRuleRequest(BaseModel):
    name: str
    trigger_event: str
    trigger_filter: dict | None = None
    action_type: str
    action_config: dict
    max_executions_per_hour: int = 100

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 200:
            raise ValueError("Name must be 1-200 characters")
        return v

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, v: str) -> str:
        if v not in VALID_ACTION_TYPES:
            raise ValueError(f"action_type must be one of: {', '.join(sorted(VALID_ACTION_TYPES))}")
        return v

    @field_validator("action_config")
    @classmethod
    def validate_action_config(cls, v: dict) -> dict:
        reject_deep_json(v, "manifest")
        reject_ctrl_json(v, "manifest")
        return v

    @field_validator("max_executions_per_hour")
    @classmethod
    def validate_max_exec(cls, v: int) -> int:
        if v < 1 or v > 10000:
            raise ValueError("max_executions_per_hour must be 1-10000")
        return v


class AutomationRuleResponse(BaseModel):
    id: str
    installation_id: str
    name: str
    trigger_event: str
    trigger_filter: dict | None
    action_type: str
    action_config: dict
    enabled: bool
    max_executions_per_hour: int
    last_executed_at: datetime | None
    execution_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── App Secret ───────────────────────────────────────────


class SetSecretRequest(BaseModel):
    key: str
    value: str
    description: str | None = None

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        import re

        v = v.strip().upper()
        if not re.match(r"^[A-Z][A-Z0-9_]{0,98}[A-Z0-9]$", v):
            raise ValueError(
                "Key must be 2-100 uppercase alphanumeric/underscores, start with letter"
            )
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        if len(v) > 10000:
            raise ValueError("Secret value must be 10000 characters or less")
        return v


class SecretMetadataResponse(BaseModel):
    """Never exposes the actual value."""

    id: str
    installation_id: str
    key: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Sandbox Execution ────────────────────────────────────


class SandboxExecutionResponse(BaseModel):
    id: str
    installation_id: str
    app_version_id: str
    function_name: str
    trigger_type: str
    trigger_event: str | None
    status: str
    duration_ms: int | None
    memory_peak_mb: float | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


# ── Review ───────────────────────────────────────────────


class SubmitForReviewRequest(BaseModel):
    app_version_id: str
    notes: str | None = None


class ReviewDecisionRequest(BaseModel):
    decision: str  # "approved" or "rejected"
    notes: str | None = None

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        if v not in {"approved", "rejected"}:
            raise ValueError("Decision must be 'approved' or 'rejected'")
        return v


class AppReviewResponse(BaseModel):
    id: str
    app_id: str
    app_version_id: str
    submitted_by: str
    review_status: str
    reviewer_id: str | None
    review_notes: str | None
    automated_checks: dict | None
    submitted_at: datetime
    reviewed_at: datetime | None

    model_config = {"from_attributes": True}


# ── Signing Key ──────────────────────────────────────────


class RegisterSigningKeyRequest(BaseModel):
    public_key: str
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 100:
            raise ValueError("Name must be 1-100 characters")
        return v


class SigningKeyResponse(BaseModel):
    id: str
    developer_id: str
    fingerprint: str
    name: str
    is_primary: bool
    revoked_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── UI Extension ─────────────────────────────────────────

VALID_SURFACES = {
    "dashboard_card",
    "project_sidebar",
    "cohort_tool",
    "submission_panel",
    "registry_detail",
    "settings_page",
    "client_portal_widget",
    "operator_console",
}


class AppUiExtensionResponse(BaseModel):
    id: str
    app_id: str
    surface: str
    title: str
    entry_path: str
    viewport_width: int | None
    viewport_height: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── OAuth ────────────────────────────────────────────────


class OAuthAuthorizeRequest(BaseModel):
    client_id: str
    redirect_uri: str
    scope: str
    state: str
    response_type: str = "code"


class OAuthTokenRequest(BaseModel):
    grant_type: str
    code: str | None = None
    client_id: str
    client_secret: str
    redirect_uri: str | None = None
    refresh_token: str | None = None


class OAuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str
