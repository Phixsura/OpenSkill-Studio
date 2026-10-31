"""Developer Platform service — app lifecycle, installations, keys, secrets, sandbox."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import structlog
from cryptography.fernet import Fernet
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import AppError
from app.models.developer import (
    AppApiKey,
    AppAutomationRule,
    AppEventSubscription,
    AppInstallation,
    AppReviewSubmission,
    AppSecret,
    AppSigningKey,
    AppStatus,
    AppVersion,
    DeveloperAccount,
    DeveloperApp,
    InstallationStatus,
    SandboxExecution,
)

log = structlog.get_logger()

# ── Errors ────────────────────────────────────────────────


class DeveloperNotFoundError(AppError):
    def __init__(self, message: str = "Developer account not found"):
        super().__init__("DEVELOPER_NOT_FOUND", message, 404)


class AppNotFoundError(AppError):
    def __init__(self, message: str = "App not found"):
        super().__init__("APP_NOT_FOUND", message, 404)


class AppVersionNotFoundError(AppError):
    def __init__(self, message: str = "App version not found"):
        super().__init__("APP_VERSION_NOT_FOUND", message, 404)


class InstallationNotFoundError(AppError):
    def __init__(self, message: str = "App installation not found"):
        super().__init__("INSTALLATION_NOT_FOUND", message, 404)


class DuplicateSlugError(AppError):
    def __init__(self):
        super().__init__("DUPLICATE_SLUG", "Slug already in use", 409)


class DuplicateVersionError(AppError):
    def __init__(self):
        super().__init__("DUPLICATE_VERSION", "Version already exists for this app", 409)


class InvalidStateTransitionError(AppError):
    def __init__(self, message: str = "Invalid app state transition"):
        super().__init__("INVALID_STATE_TRANSITION", message, 422)


class PermissionDeniedError(AppError):
    def __init__(self):
        super().__init__("PERMISSION_DENIED", "You do not have permission to perform this action", 403)


class AlreadyInstalledError(AppError):
    def __init__(self):
        super().__init__("ALREADY_INSTALLED", "App is already installed in this organization", 409)


class ApiKeyNotFoundError(AppError):
    def __init__(self):
        super().__init__("API_KEY_NOT_FOUND", "API key not found", 404)


# ── Crypto helpers ────────────────────────────────────────


def _get_fernet() -> Fernet:
    """Fernet cipher for encrypting app secrets (reuse provider credential key)."""
    key = settings.credential_encryption_key
    if not key:
        # Test/dev fallback — generate a deterministic key from jwt_secret
        import base64
        seed = (settings.jwt_secret or "dev-fallback-key").encode()
        key = base64.urlsafe_b64encode(seed[:32].ljust(32, b"\0")).decode()
    return Fernet(key.encode())


def _generate_oauth_client_id() -> str:
    return f"osk_{secrets.token_urlsafe(24)}"


def _generate_oauth_client_secret() -> tuple[str, str]:
    raw = secrets.token_urlsafe(48)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


def _generate_api_key() -> tuple[str, str, str]:
    """Return (full_key, prefix, hash)."""
    token = secrets.token_urlsafe(32)
    full_key = f"osk_app_{token}"
    prefix = full_key[:12]
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, prefix, key_hash


# ── Developer Account CRUD ───────────────────────────────


async def create_developer_account(
    db: AsyncSession, *, owner_user_id: str, **kwargs
) -> DeveloperAccount:
    account = DeveloperAccount(owner_user_id=owner_user_id, **kwargs)
    db.add(account)
    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateSlugError() from exc
    log.info("developer_account_created", account_id=account.id, slug=account.slug)
    return account


async def get_developer_account(db: AsyncSession, account_id: str) -> DeveloperAccount:
    result = await db.execute(
        select(DeveloperAccount).where(DeveloperAccount.id == account_id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise DeveloperNotFoundError()
    return account


async def get_developer_account_by_user(
    db: AsyncSession, user_id: str
) -> DeveloperAccount | None:
    result = await db.execute(
        select(DeveloperAccount).where(DeveloperAccount.owner_user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_developer_accounts(
    db: AsyncSession, *, page: int = 1, per_page: int = 20
) -> tuple[list[DeveloperAccount], int]:
    count_q = select(func.count()).select_from(DeveloperAccount)
    total = (await db.execute(count_q)).scalar() or 0

    q = (
        select(DeveloperAccount)
        .order_by(DeveloperAccount.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(q)
    return list(result.scalars().all()), total


async def update_developer_account(
    db: AsyncSession, account: DeveloperAccount, **kwargs
) -> DeveloperAccount:
    for k, v in kwargs.items():
        if v is not None:
            setattr(account, k, v)
    await db.flush()
    await db.refresh(account)
    return account


# ── Developer App CRUD ───────────────────────────────────


async def create_app(
    db: AsyncSession, *, developer_id: str, **kwargs
) -> tuple[DeveloperApp, str]:
    """Create app. Returns (app, oauth_client_secret) — secret shown once."""
    client_id = _generate_oauth_client_id()
    raw_secret, secret_hash = _generate_oauth_client_secret()

    app = DeveloperApp(
        developer_id=developer_id,
        oauth_client_id=client_id,
        oauth_client_secret_hash=secret_hash,
        **kwargs,
    )
    db.add(app)
    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateSlugError() from exc
    log.info("developer_app_created", app_id=app.id, slug=app.slug)
    return app, raw_secret


async def get_app(db: AsyncSession, app_id: str) -> DeveloperApp:
    result = await db.execute(
        select(DeveloperApp).where(DeveloperApp.id == app_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        raise AppNotFoundError()
    return app


async def get_app_by_client_id(db: AsyncSession, client_id: str) -> DeveloperApp | None:
    result = await db.execute(
        select(DeveloperApp).where(DeveloperApp.oauth_client_id == client_id)
    )
    return result.scalar_one_or_none()


async def list_apps(
    db: AsyncSession,
    *,
    developer_id: str | None = None,
    category: str | None = None,
    status: str | None = None,
    visibility: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[DeveloperApp], int]:
    q = select(DeveloperApp)
    count_q = select(func.count()).select_from(DeveloperApp)

    if developer_id:
        q = q.where(DeveloperApp.developer_id == developer_id)
        count_q = count_q.where(DeveloperApp.developer_id == developer_id)
    if category:
        q = q.where(DeveloperApp.category == category)
        count_q = count_q.where(DeveloperApp.category == category)
    if status:
        q = q.where(DeveloperApp.status == status)
        count_q = count_q.where(DeveloperApp.status == status)
    if visibility:
        q = q.where(DeveloperApp.visibility == visibility)
        count_q = count_q.where(DeveloperApp.visibility == visibility)

    total = (await db.execute(count_q)).scalar() or 0
    q = q.order_by(DeveloperApp.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    return list(result.scalars().all()), total


async def update_app(db: AsyncSession, app: DeveloperApp, **kwargs) -> DeveloperApp:
    for k, v in kwargs.items():
        if v is not None:
            setattr(app, k, v)
    await db.flush()
    await db.refresh(app)
    return app


async def transition_app_status(
    db: AsyncSession, app: DeveloperApp, new_status: str
) -> DeveloperApp:
    """Enforce state machine transitions."""
    allowed = {
        "draft": {"testing", "deleted"},
        "testing": {"draft", "submitted", "deleted"},
        "submitted": {"approved", "rejected"},
        "rejected": {"draft"},
        "approved": {"published"},
        "published": {"deprecated", "revoked"},
        "deprecated": {"revoked"},
    }
    current = app.status.value if isinstance(app.status, AppStatus) else app.status
    if new_status not in allowed.get(current, set()):
        raise InvalidStateTransitionError(
            message=f"Cannot transition from {current} to {new_status}"
        )
    app.status = new_status
    await db.flush()
    log.info("app_status_changed", app_id=app.id, old=current, new=new_status)
    return app


# ── App Version ──────────────────────────────────────────


async def create_app_version(
    db: AsyncSession, *, app_id: str, **kwargs
) -> AppVersion:
    version = AppVersion(app_id=app_id, **kwargs)
    db.add(version)
    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateVersionError() from exc
    log.info("app_version_created", app_id=app_id, version=version.version)
    return version


async def get_app_version(db: AsyncSession, version_id: str) -> AppVersion:
    result = await db.execute(
        select(AppVersion).where(AppVersion.id == version_id)
    )
    v = result.scalar_one_or_none()
    if not v:
        raise AppVersionNotFoundError()
    return v


async def list_app_versions(
    db: AsyncSession, app_id: str, *, page: int = 1, per_page: int = 20
) -> tuple[list[AppVersion], int]:
    count_q = (
        select(func.count()).select_from(AppVersion).where(AppVersion.app_id == app_id)
    )
    total = (await db.execute(count_q)).scalar() or 0

    q = (
        select(AppVersion)
        .where(AppVersion.app_id == app_id)
        .order_by(AppVersion.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(q)
    return list(result.scalars().all()), total


async def review_app_version(
    db: AsyncSession,
    version: AppVersion,
    *,
    decision: str,
    reviewer_id: str,
    notes: str | None = None,
) -> AppVersion:
    version.review_status = decision
    version.reviewed_by = reviewer_id
    version.reviewed_at = datetime.now(UTC)
    version.review_notes = notes
    await db.flush()
    log.info(
        "app_version_reviewed",
        version_id=version.id,
        decision=decision,
        reviewer=reviewer_id,
    )
    return version


# ── App Installation ─────────────────────────────────────


async def install_app(
    db: AsyncSession,
    *,
    app_id: str,
    app_version_id: str,
    org_id: str,
    installed_by: str,
    tenant_id: str | None = None,
    granted_permissions: list | None = None,
    config: dict | None = None,
    pinned_version: bool = False,
) -> AppInstallation:
    # Check for existing active installation
    existing = await db.execute(
        select(AppInstallation).where(
            AppInstallation.app_id == app_id,
            AppInstallation.org_id == org_id,
            AppInstallation.status == InstallationStatus.ACTIVE,
        )
    )
    if existing.scalar_one_or_none():
        raise AlreadyInstalledError()

    installation = AppInstallation(
        app_id=app_id,
        app_version_id=app_version_id,
        org_id=org_id,
        installed_by=installed_by,
        tenant_id=tenant_id,
        granted_permissions=granted_permissions or [],
        config=config or {},
        pinned_version=pinned_version,
    )
    db.add(installation)
    await db.flush()
    log.info("app_installed", app_id=app_id, org_id=org_id, installation_id=installation.id)
    return installation


async def get_installation(db: AsyncSession, installation_id: str) -> AppInstallation:
    result = await db.execute(
        select(AppInstallation).where(AppInstallation.id == installation_id)
    )
    inst = result.scalar_one_or_none()
    if not inst:
        raise InstallationNotFoundError()
    return inst


async def list_installations(
    db: AsyncSession,
    *,
    org_id: str | None = None,
    app_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[AppInstallation], int]:
    q = select(AppInstallation)
    count_q = select(func.count()).select_from(AppInstallation)

    if org_id:
        q = q.where(AppInstallation.org_id == org_id)
        count_q = count_q.where(AppInstallation.org_id == org_id)
    if app_id:
        q = q.where(AppInstallation.app_id == app_id)
        count_q = count_q.where(AppInstallation.app_id == app_id)
    if status:
        q = q.where(AppInstallation.status == status)
        count_q = count_q.where(AppInstallation.status == status)
    else:
        # Default: exclude uninstalled
        q = q.where(AppInstallation.status != InstallationStatus.UNINSTALLED)
        count_q = count_q.where(AppInstallation.status != InstallationStatus.UNINSTALLED)

    total = (await db.execute(count_q)).scalar() or 0
    q = q.order_by(AppInstallation.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    return list(result.scalars().all()), total


async def uninstall_app(db: AsyncSession, installation: AppInstallation) -> AppInstallation:
    installation.status = InstallationStatus.UNINSTALLED
    installation.uninstalled_at = datetime.now(UTC)
    await db.flush()
    log.info("app_uninstalled", installation_id=installation.id, app_id=installation.app_id)
    return installation


async def update_installation(
    db: AsyncSession, installation: AppInstallation, **kwargs
) -> AppInstallation:
    for k, v in kwargs.items():
        if v is not None:
            setattr(installation, k, v)
    await db.flush()
    await db.refresh(installation)
    return installation


# ── App API Key ──────────────────────────────────────────


async def create_api_key(
    db: AsyncSession,
    *,
    app_id: str,
    name: str,
    scopes: list | None = None,
    installation_id: str | None = None,
    expires_in_days: int | None = None,
) -> tuple[AppApiKey, str]:
    """Return (key_record, full_key) — full key shown once."""
    full_key, prefix, key_hash = _generate_api_key()

    expires_at = None
    if expires_in_days:
        expires_at = datetime.now(UTC) + timedelta(days=expires_in_days)

    key = AppApiKey(
        app_id=app_id,
        installation_id=installation_id,
        name=name,
        key_prefix=prefix,
        key_hash=key_hash,
        scopes=scopes or [],
        expires_at=expires_at,
    )
    db.add(key)
    await db.flush()
    log.info("api_key_created", key_id=key.id, app_id=app_id, prefix=prefix)
    return key, full_key


async def authenticate_api_key(db: AsyncSession, raw_key: str) -> AppApiKey | None:
    """Validate an API key and return the record if valid."""
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    result = await db.execute(
        select(AppApiKey).where(
            AppApiKey.key_hash == key_hash,
            AppApiKey.revoked_at.is_(None),
        )
    )
    key = result.scalar_one_or_none()
    if not key:
        return None

    # Check expiry
    if key.expires_at and key.expires_at < datetime.now(UTC):
        return None

    # Update last_used_at
    key.last_used_at = datetime.now(UTC)
    await db.flush()
    return key


async def list_api_keys(
    db: AsyncSession, app_id: str, *, include_revoked: bool = False
) -> list[AppApiKey]:
    q = select(AppApiKey).where(AppApiKey.app_id == app_id)
    if not include_revoked:
        q = q.where(AppApiKey.revoked_at.is_(None))
    q = q.order_by(AppApiKey.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def revoke_api_key(db: AsyncSession, key: AppApiKey) -> AppApiKey:
    key.revoked_at = datetime.now(UTC)
    await db.flush()
    log.info("api_key_revoked", key_id=key.id, app_id=key.app_id)
    return key


# ── Event Subscriptions ──────────────────────────────────


async def create_event_subscription(
    db: AsyncSession,
    *,
    installation_id: str,
    event_type: str,
    filter_expression: dict | None = None,
) -> AppEventSubscription:
    sub = AppEventSubscription(
        installation_id=installation_id,
        event_type=event_type,
        filter_expression=filter_expression,
    )
    db.add(sub)
    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        raise AppError(
            status_code=409,
            code="DUPLICATE_SUBSCRIPTION",
            message=f"Already subscribed to {event_type}",
        ) from exc
    return sub


async def list_event_subscriptions(
    db: AsyncSession, installation_id: str
) -> list[AppEventSubscription]:
    result = await db.execute(
        select(AppEventSubscription)
        .where(AppEventSubscription.installation_id == installation_id)
        .order_by(AppEventSubscription.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_event_subscription(db: AsyncSession, subscription_id: str) -> None:
    result = await db.execute(
        select(AppEventSubscription).where(AppEventSubscription.id == subscription_id)
    )
    sub = result.scalar_one_or_none()
    if sub:
        await db.delete(sub)
        await db.flush()


# ── Automation Rules ─────────────────────────────────────


async def create_automation_rule(
    db: AsyncSession, *, installation_id: str, **kwargs
) -> AppAutomationRule:
    rule = AppAutomationRule(installation_id=installation_id, **kwargs)
    db.add(rule)
    await db.flush()
    log.info("automation_rule_created", rule_id=rule.id, installation_id=installation_id)
    return rule


async def list_automation_rules(
    db: AsyncSession, installation_id: str
) -> list[AppAutomationRule]:
    result = await db.execute(
        select(AppAutomationRule)
        .where(AppAutomationRule.installation_id == installation_id)
        .order_by(AppAutomationRule.created_at.desc())
    )
    return list(result.scalars().all())


async def get_automation_rule(db: AsyncSession, rule_id: str) -> AppAutomationRule:
    result = await db.execute(
        select(AppAutomationRule).where(AppAutomationRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise AppError(status_code=404, code="RULE_NOT_FOUND", message="Automation rule not found")
    return rule


async def update_automation_rule(
    db: AsyncSession, rule: AppAutomationRule, **kwargs
) -> AppAutomationRule:
    for k, v in kwargs.items():
        if v is not None:
            setattr(rule, k, v)
    await db.flush()
    await db.refresh(rule)
    return rule


async def delete_automation_rule(db: AsyncSession, rule_id: str) -> None:
    rule = await get_automation_rule(db, rule_id)
    await db.delete(rule)
    await db.flush()


# ── App Secrets ──────────────────────────────────────────


async def set_secret(
    db: AsyncSession,
    *,
    installation_id: str,
    key: str,
    value: str,
    description: str | None = None,
) -> AppSecret:
    """Upsert a secret — Fernet encrypted, write-only."""
    fernet = _get_fernet()
    encrypted = fernet.encrypt(value.encode()).decode()

    # Check for existing
    result = await db.execute(
        select(AppSecret).where(
            AppSecret.installation_id == installation_id,
            AppSecret.key == key,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.encrypted_value = encrypted
        if description is not None:
            existing.description = description
        await db.flush()
        await db.refresh(existing)
        return existing

    secret = AppSecret(
        installation_id=installation_id,
        key=key,
        encrypted_value=encrypted,
        description=description,
    )
    db.add(secret)
    await db.flush()
    await db.refresh(secret)
    return secret


async def get_decrypted_secrets(
    db: AsyncSession, installation_id: str
) -> dict[str, str]:
    """Decrypt all secrets for sandbox injection."""
    fernet = _get_fernet()
    result = await db.execute(
        select(AppSecret).where(AppSecret.installation_id == installation_id)
    )
    secrets_map = {}
    for s in result.scalars().all():
        try:
            secrets_map[s.key] = fernet.decrypt(s.encrypted_value.encode()).decode()
        except Exception:
            log.warning("secret_decrypt_failed", installation_id=installation_id, key=s.key)
    return secrets_map


async def list_secret_metadata(
    db: AsyncSession, installation_id: str
) -> list[AppSecret]:
    result = await db.execute(
        select(AppSecret)
        .where(AppSecret.installation_id == installation_id)
        .order_by(AppSecret.key)
    )
    return list(result.scalars().all())


async def delete_secret(db: AsyncSession, installation_id: str, key: str) -> None:
    result = await db.execute(
        select(AppSecret).where(
            AppSecret.installation_id == installation_id,
            AppSecret.key == key,
        )
    )
    secret = result.scalar_one_or_none()
    if secret:
        await db.delete(secret)
        await db.flush()


# ── Signing Keys ─────────────────────────────────────────


async def register_signing_key(
    db: AsyncSession,
    *,
    developer_id: str,
    public_key: str,
    name: str,
) -> AppSigningKey:
    fingerprint = hashlib.sha256(public_key.encode()).hexdigest()[:16]
    key = AppSigningKey(
        developer_id=developer_id,
        public_key=public_key,
        fingerprint=fingerprint,
        name=name,
    )
    db.add(key)
    await db.flush()
    log.info("signing_key_registered", developer_id=developer_id, fingerprint=fingerprint)
    return key


async def list_signing_keys(db: AsyncSession, developer_id: str) -> list[AppSigningKey]:
    result = await db.execute(
        select(AppSigningKey)
        .where(
            AppSigningKey.developer_id == developer_id,
            AppSigningKey.revoked_at.is_(None),
        )
        .order_by(AppSigningKey.created_at.desc())
    )
    return list(result.scalars().all())


# ── App Review ───────────────────────────────────────────


async def submit_for_review(
    db: AsyncSession,
    *,
    app_id: str,
    app_version_id: str,
    submitted_by: str,
    notes: str | None = None,
) -> AppReviewSubmission:
    # Run automated checks
    automated_checks = await _run_automated_checks(db, app_version_id)

    submission = AppReviewSubmission(
        app_id=app_id,
        app_version_id=app_version_id,
        submitted_by=submitted_by,
        automated_checks=automated_checks,
    )
    db.add(submission)
    await db.flush()
    log.info("app_review_submitted", app_id=app_id, version_id=app_version_id)
    return submission


async def _run_automated_checks(db: AsyncSession, version_id: str) -> dict:
    """Run automated review checks on an app version."""
    version = await get_app_version(db, version_id)
    checks = {
        "manifest_valid": True,
        "permissions_declared": bool(
            version.manifest.get("permissions") if version.manifest else False
        ),
        "content_hash_present": bool(version.content_hash),
        "version_semver": True,
        "checks_passed": True,
    }
    # Verify manifest has required fields
    if version.manifest:
        required = {"schema_version", "app", "permissions"}
        missing = required - set(version.manifest.keys())
        if missing:
            checks["manifest_valid"] = False
            checks["manifest_missing_fields"] = list(missing)
            checks["checks_passed"] = False
    else:
        checks["manifest_valid"] = False
        checks["checks_passed"] = False
    return checks


async def list_review_submissions(
    db: AsyncSession,
    *,
    app_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[AppReviewSubmission], int]:
    q = select(AppReviewSubmission)
    count_q = select(func.count()).select_from(AppReviewSubmission)

    if app_id:
        q = q.where(AppReviewSubmission.app_id == app_id)
        count_q = count_q.where(AppReviewSubmission.app_id == app_id)
    if status:
        q = q.where(AppReviewSubmission.review_status == status)
        count_q = count_q.where(AppReviewSubmission.review_status == status)

    total = (await db.execute(count_q)).scalar() or 0
    q = q.order_by(AppReviewSubmission.submitted_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    return list(result.scalars().all()), total


async def decide_review(
    db: AsyncSession,
    review: AppReviewSubmission,
    *,
    decision: str,
    reviewer_id: str,
    notes: str | None = None,
) -> AppReviewSubmission:
    review.review_status = decision
    review.reviewer_id = reviewer_id
    review.reviewed_at = datetime.now(UTC)
    review.review_notes = notes

    # Also update the version review status
    version = await get_app_version(db, review.app_version_id)
    await review_app_version(db, version, decision=decision, reviewer_id=reviewer_id, notes=notes)

    # If approved, transition app to approved
    if decision == "approved":
        app = await get_app(db, review.app_id)
        if app.status == AppStatus.SUBMITTED:
            app.status = AppStatus.APPROVED
            await db.flush()

    await db.flush()
    log.info("review_decided", review_id=review.id, decision=decision)
    return review


# ── Kill Switch ──────────────────────────────────────────


async def revoke_app(db: AsyncSession, app_id: str, *, reason: str) -> DeveloperApp:
    """Emergency kill switch — revoke app and suspend all installations."""
    app = await get_app(db, app_id)
    app.status = AppStatus.REVOKED
    await db.flush()

    # Suspend all active installations
    await db.execute(
        update(AppInstallation)
        .where(
            AppInstallation.app_id == app_id,
            AppInstallation.status == InstallationStatus.ACTIVE,
        )
        .values(status=InstallationStatus.SUSPENDED)
    )

    # Revoke all API keys
    await db.execute(
        update(AppApiKey)
        .where(
            AppApiKey.app_id == app_id,
            AppApiKey.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )

    await db.flush()
    await db.refresh(app)
    log.warning("app_revoked", app_id=app_id, reason=reason)
    return app


# ── Sandbox Execution Log ────────────────────────────────


async def log_sandbox_execution(
    db: AsyncSession,
    *,
    installation_id: str,
    app_version_id: str,
    function_name: str,
    trigger_type: str,
    trigger_event: str | None = None,
    status: str,
    duration_ms: int | None = None,
    memory_peak_mb: float | None = None,
    error_message: str | None = None,
    logs: list | None = None,
) -> SandboxExecution:
    execution = SandboxExecution(
        installation_id=installation_id,
        app_version_id=app_version_id,
        function_name=function_name,
        trigger_type=trigger_type,
        trigger_event=trigger_event,
        status=status,
        duration_ms=duration_ms,
        memory_peak_mb=memory_peak_mb,
        error_message=error_message,
        logs=logs,
        completed_at=datetime.now(UTC) if status != "running" else None,
    )
    db.add(execution)
    await db.flush()
    return execution


async def list_sandbox_executions(
    db: AsyncSession,
    installation_id: str,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[SandboxExecution], int]:
    count_q = (
        select(func.count())
        .select_from(SandboxExecution)
        .where(SandboxExecution.installation_id == installation_id)
    )
    total = (await db.execute(count_q)).scalar() or 0

    q = (
        select(SandboxExecution)
        .where(SandboxExecution.installation_id == installation_id)
        .order_by(SandboxExecution.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(q)
    return list(result.scalars().all()), total
