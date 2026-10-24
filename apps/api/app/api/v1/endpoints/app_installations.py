"""App installation, secrets, event subscriptions, and automation endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.developer import (
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    AppInstallationResponse,
    AutomationRuleResponse,
    CreateApiKeyRequest,
    CreateAutomationRuleRequest,
    CreateEventSubscriptionRequest,
    EventSubscriptionResponse,
    InstallAppRequest,
    SandboxExecutionResponse,
    SecretMetadataResponse,
    SetSecretRequest,
    UpdateInstallationRequest,
)
from app.services import developer as dev_svc

router = APIRouter(tags=["App Installations"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── Install / Uninstall ──────────────────────────────────


@router.post(
    "/orgs/{org_id}/apps/install",
    response_model=DataResponse[AppInstallationResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def install_app(
    org_id: str,
    body: InstallAppRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Install an app into an organization."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)

    app = await dev_svc.get_app(db, body.app_id)
    version_id = body.app_version_id
    if not version_id:
        versions, _ = await dev_svc.list_app_versions(db, app.id, per_page=1)
        if versions:
            version_id = versions[0].id
        else:
            raise dev_svc.AppVersionNotFoundError(
                message="No versions available for this app"
            )

    installation = await dev_svc.install_app(
        db,
        app_id=body.app_id,
        app_version_id=version_id,
        org_id=org_id,
        installed_by=user.id,
        granted_permissions=body.granted_permissions,
        config=body.config,
        pinned_version=body.pinned_version,
    )
    await db.commit()
    return DataResponse(data=AppInstallationResponse.model_validate(installation))


@router.get(
    "/orgs/{org_id}/apps/installations",
    response_model=ListResponse[AppInstallationResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_org_installations(
    org_id: str,
    status: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List installed apps for an organization."""
    await require_org_member(org_id, user, db)
    installations, total = await dev_svc.list_installations(
        db, org_id=org_id, status=status, page=page, per_page=per_page
    )
    return ListResponse(
        data=[AppInstallationResponse.model_validate(i) for i in installations],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.get(
    "/orgs/{org_id}/apps/installations/{installation_id}",
    response_model=DataResponse[AppInstallationResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def get_installation(
    org_id: str,
    installation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get installation details."""
    await require_org_member(org_id, user, db)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    return DataResponse(data=AppInstallationResponse.model_validate(installation))


@router.patch(
    "/orgs/{org_id}/apps/installations/{installation_id}",
    response_model=DataResponse[AppInstallationResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def update_installation(
    org_id: str,
    installation_id: str,
    body: UpdateInstallationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update installation config."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    updates = body.model_dump(exclude_unset=True)
    installation = await dev_svc.update_installation(db, installation, **updates)
    await db.commit()
    return DataResponse(data=AppInstallationResponse.model_validate(installation))


@router.post(
    "/orgs/{org_id}/apps/installations/{installation_id}/upgrade",
    response_model=DataResponse[AppInstallationResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def upgrade_installation(
    org_id: str,
    installation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upgrade an installation to the latest app version."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()

    # Find latest version for the app
    versions, _ = await dev_svc.list_app_versions(db, installation.app_id, per_page=1)
    if not versions:
        raise dev_svc.AppVersionNotFoundError(message="No versions available")
    latest = versions[0]

    if installation.app_version_id == latest.id:
        return DataResponse(data=AppInstallationResponse.model_validate(installation))

    installation = await dev_svc.update_installation(
        db, installation, app_version_id=latest.id
    )
    await db.commit()
    return DataResponse(data=AppInstallationResponse.model_validate(installation))


@router.delete(
    "/orgs/{org_id}/apps/installations/{installation_id}",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def uninstall_app(
    org_id: str,
    installation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Uninstall an app from an organization."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    await dev_svc.uninstall_app(db, installation)
    await db.commit()
    return DataResponse(data={"status": "uninstalled"})


# ── Secrets ──────────────────────────────────────────────


@router.put(
    "/orgs/{org_id}/apps/installations/{installation_id}/secrets",
    response_model=DataResponse[SecretMetadataResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def set_secret(
    org_id: str,
    installation_id: str,
    body: SetSecretRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Set or update an app secret (write-only, Fernet encrypted)."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    secret = await dev_svc.set_secret(
        db,
        installation_id=installation_id,
        key=body.key,
        value=body.value,
        description=body.description,
    )
    await db.commit()
    return DataResponse(data=SecretMetadataResponse.model_validate(secret))


@router.get(
    "/orgs/{org_id}/apps/installations/{installation_id}/secrets",
    response_model=DataResponse[list[SecretMetadataResponse]],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_secrets(
    org_id: str,
    installation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List secret metadata (never exposes values)."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    secrets = await dev_svc.list_secret_metadata(db, installation_id)
    return DataResponse(data=[SecretMetadataResponse.model_validate(s) for s in secrets])


@router.delete(
    "/orgs/{org_id}/apps/installations/{installation_id}/secrets/{key}",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def delete_secret(
    org_id: str,
    installation_id: str,
    key: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete an app secret."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    await dev_svc.delete_secret(db, installation_id, key)
    await db.commit()
    return DataResponse(data={"status": "deleted"})


# ── Event Subscriptions ──────────────────────────────────


@router.post(
    "/orgs/{org_id}/apps/installations/{installation_id}/events",
    response_model=DataResponse[EventSubscriptionResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def create_event_subscription(
    org_id: str,
    installation_id: str,
    body: CreateEventSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Subscribe to a platform event."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    sub = await dev_svc.create_event_subscription(
        db,
        installation_id=installation_id,
        event_type=body.event_type,
        filter_expression=body.filter_expression,
    )
    await db.commit()
    return DataResponse(data=EventSubscriptionResponse.model_validate(sub))


@router.get(
    "/orgs/{org_id}/apps/installations/{installation_id}/events",
    response_model=DataResponse[list[EventSubscriptionResponse]],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_event_subscriptions(
    org_id: str,
    installation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List event subscriptions for an installation."""
    await require_org_member(org_id, user, db)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    subs = await dev_svc.list_event_subscriptions(db, installation_id)
    return DataResponse(data=[EventSubscriptionResponse.model_validate(s) for s in subs])


@router.delete(
    "/orgs/{org_id}/apps/installations/{installation_id}/events/{subscription_id}",
    dependencies=[Depends(rate_limit(30, 60))],
)
async def delete_event_subscription(
    org_id: str,
    installation_id: str,
    subscription_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Remove an event subscription."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    # Verify subscription belongs to this installation
    from sqlalchemy import select

    from app.models.developer import AppEventSubscription

    result = await db.execute(
        select(AppEventSubscription).where(
            AppEventSubscription.id == subscription_id,
            AppEventSubscription.installation_id == installation_id,
        )
    )
    if not result.scalar_one_or_none():
        from app.exceptions import AppError

        raise AppError("SUBSCRIPTION_NOT_FOUND", "Event subscription not found", 404)
    await dev_svc.delete_event_subscription(db, subscription_id)
    await db.commit()
    return DataResponse(data={"status": "deleted"})


# ── Automation Rules ─────────────────────────────────────


@router.post(
    "/orgs/{org_id}/apps/installations/{installation_id}/rules",
    response_model=DataResponse[AutomationRuleResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_automation_rule(
    org_id: str,
    installation_id: str,
    body: CreateAutomationRuleRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create an event → action automation rule."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    rule = await dev_svc.create_automation_rule(
        db,
        installation_id=installation_id,
        name=body.name,
        trigger_event=body.trigger_event,
        trigger_filter=body.trigger_filter,
        action_type=body.action_type,
        action_config=body.action_config,
        max_executions_per_hour=body.max_executions_per_hour,
    )
    await db.commit()
    return DataResponse(data=AutomationRuleResponse.model_validate(rule))


@router.get(
    "/orgs/{org_id}/apps/installations/{installation_id}/rules",
    response_model=DataResponse[list[AutomationRuleResponse]],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_automation_rules(
    org_id: str,
    installation_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List automation rules for an installation."""
    await require_org_member(org_id, user, db)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    rules = await dev_svc.list_automation_rules(db, installation_id)
    return DataResponse(data=[AutomationRuleResponse.model_validate(r) for r in rules])


@router.delete(
    "/orgs/{org_id}/apps/installations/{installation_id}/rules/{rule_id}",
    dependencies=[Depends(rate_limit(20, 60))],
)
async def delete_automation_rule(
    org_id: str,
    installation_id: str,
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete an automation rule."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    # Verify rule belongs to this installation
    from sqlalchemy import select

    from app.models.developer import AppAutomationRule

    result = await db.execute(
        select(AppAutomationRule).where(
            AppAutomationRule.id == rule_id,
            AppAutomationRule.installation_id == installation_id,
        )
    )
    if not result.scalar_one_or_none():
        from app.exceptions import AppError

        raise AppError("RULE_NOT_FOUND", "Automation rule not found", 404)
    await dev_svc.delete_automation_rule(db, rule_id)
    await db.commit()
    return DataResponse(data={"status": "deleted"})


# ── Sandbox Executions ───────────────────────────────────


@router.get(
    "/orgs/{org_id}/apps/installations/{installation_id}/executions",
    response_model=ListResponse[SandboxExecutionResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_sandbox_executions(
    org_id: str,
    installation_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List sandbox execution logs for an installation."""
    await require_org_member(org_id, user, db)
    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()
    executions, total = await dev_svc.list_sandbox_executions(
        db, installation_id, page=page, per_page=per_page
    )
    return ListResponse(
        data=[SandboxExecutionResponse.model_validate(e) for e in executions],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


# ── API Keys ────────────────────────────────────────────


@router.post(
    "/developer/apps/{app_id}/api-keys",
    response_model=DataResponse[ApiKeyCreatedResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_api_key(
    app_id: str,
    body: CreateApiKeyRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create an API key for an app (full key shown once)."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    key_record, full_key = await dev_svc.create_api_key(
        db,
        app_id=app_id,
        name=body.name,
        scopes=body.scopes,
        installation_id=body.installation_id,
        expires_in_days=body.expires_in_days,
    )
    await db.commit()
    return DataResponse(
        data=ApiKeyCreatedResponse(
            id=key_record.id,
            key=full_key,
            key_prefix=key_record.key_prefix,
            name=key_record.name,
            scopes=key_record.scopes,
            expires_at=key_record.expires_at,
        )
    )


@router.get(
    "/developer/apps/{app_id}/api-keys",
    response_model=DataResponse[list[ApiKeyResponse]],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_api_keys(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List API keys for an app."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()
    keys = await dev_svc.list_api_keys(db, app_id)
    return DataResponse(data=[ApiKeyResponse.model_validate(k) for k in keys])


@router.delete(
    "/developer/apps/{app_id}/api-keys/{key_id}",
    dependencies=[Depends(rate_limit(10, 60))],
)
async def revoke_api_key(
    app_id: str,
    key_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Revoke an API key."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    from sqlalchemy import select

    from app.models.developer import AppApiKey

    result = await db.execute(
        select(AppApiKey).where(AppApiKey.id == key_id, AppApiKey.app_id == app_id)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise dev_svc.ApiKeyNotFoundError()
    await dev_svc.revoke_api_key(db, key)
    await db.commit()
    return DataResponse(data={"status": "revoked"})
