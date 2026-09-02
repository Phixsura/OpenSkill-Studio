"""Tenant branding validation + persistence (ADR-014 §10.1).

NO arbitrary HTML/JS anywhere: closed theme-token keys (hex colors + a
bounded radius enum), plain-text strings, https-only URLs.
"""

import re

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.branding import (
    THEME_COLOR_KEYS,
    THEME_RADIUS_VALUES,
    TenantBranding,
)
from app.controlplane.services.audit import Actor, record_audit
from app.exceptions import AppError

log = structlog.get_logger()

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
MAX_LEGAL_LINKS = 5


def validate_theme_tokens(tokens: dict) -> dict:
    for key, value in tokens.items():
        if key == "radius":
            # R47[29]: `value not in <set>` raises TypeError for unhashable
            # values (a dict/list radius) → 500 instead of 422. Type-check first.
            if not isinstance(value, str) or value not in THEME_RADIUS_VALUES:
                raise AppError(
                    "BRANDING_INVALID",
                    f"radius must be one of {sorted(THEME_RADIUS_VALUES)}",
                    422,
                )
        elif key in THEME_COLOR_KEYS:
            if not isinstance(value, str) or not _HEX_RE.match(value):
                raise AppError("BRANDING_INVALID", f"theme token '{key}' must be #RRGGBB", 422)
        else:
            raise AppError("BRANDING_INVALID", f"Unknown theme token '{key}'", 422)
    return tokens


def validate_https_url(url: str | None, field: str) -> str | None:
    if url is None:
        return None
    if not url.startswith("https://") or len(url) > 500:
        raise AppError("BRANDING_INVALID", f"{field} must be an https:// URL", 422)
    return url


def validate_legal_links(links: list) -> list:
    if len(links) > MAX_LEGAL_LINKS:
        raise AppError("BRANDING_INVALID", f"At most {MAX_LEGAL_LINKS} legal links", 422)
    for link in links:
        if not isinstance(link, dict) or set(link.keys()) != {"label", "url"}:
            raise AppError("BRANDING_INVALID", "legal_links entries need label+url only", 422)
        if not isinstance(link["label"], str) or len(link["label"]) > 50:
            raise AppError("BRANDING_INVALID", "legal link label too long", 422)
        validate_https_url(link["url"], "legal link url")
    return links


async def upsert_branding(
    db: AsyncSession, tenant_id: str, updates: dict, *, actor: Actor
) -> TenantBranding:
    if "theme_tokens" in updates:
        validate_theme_tokens(updates["theme_tokens"] or {})
    if "support_url" in updates:
        validate_https_url(updates["support_url"], "support_url")
    if "legal_links" in updates:
        validate_legal_links(updates["legal_links"] or [])
    branding = (
        await db.execute(select(TenantBranding).where(TenantBranding.tenant_id == tenant_id))
    ).scalar_one_or_none()
    if branding is None:
        branding = TenantBranding(tenant_id=tenant_id, updated_by=actor.user_id)
        db.add(branding)
    for field, value in updates.items():
        setattr(branding, field, value)
    branding.updated_by = actor.user_id
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="branding.updated",
        target_type="tenant",
        target_id=tenant_id,
        tenant_id=tenant_id,
        after={"fields": sorted(updates.keys())},
    )
    return branding
