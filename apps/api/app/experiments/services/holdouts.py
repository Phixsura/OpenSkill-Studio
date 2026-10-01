"""Global holdout groups (ADR-017 §4.12 v2).

A holdout group withholds a deterministic band of units from NEW enrollment
into every experiment of its domain (platform-wide, or one org's experiments
when scoped) — the long-term counterfactual for "everything we shipped".

Semantics (pinned by tests):
- Membership is computed from a dedicated salt (``holdout-group:<key>``) and
  never stored — releasing a group instantly frees its units.
- Only NEW enrollment is blocked; existing sticky assignments keep serving
  (a holdout never yanks a served experience — same rule as pause).
- Exclusion happens before any per-experiment roll, so group members simply
  see the default experience across the whole domain.

Hot-path note: resolution consults active groups per domain, so the lookup
is cached in-process (60s TTL, same pattern as the missing-key cache) and
invalidated eagerly on create/release in this process.
"""

import time
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.experiments.models import HoldoutGroup
from app.experiments.models.holdout import HOLDOUT_GROUP_MAX_BP
from app.experiments.security import EXPERIMENT_DOMAINS
from app.models.organization import Organization

_GROUP_CACHE_TTL_SECONDS = 60.0
# domain -> (expiry, [(key, holdout_bp, scope_org_id, ends_at), ...])
_GROUP_CACHE: dict[str, tuple[float, list[tuple[str, int, str | None, datetime | None]]]] = {}


def invalidate_holdout_group_cache() -> None:
    _GROUP_CACHE.clear()


async def active_holdout_groups(
    db: AsyncSession, domain: str
) -> list[tuple[str, int, str | None, datetime | None]]:
    """Active groups for a domain, cached. ends_at is re-checked at eval
    time so an expired group stops excluding without a status write."""
    cached = _GROUP_CACHE.get(domain)
    now_mono = time.monotonic()
    if cached is not None and cached[0] > now_mono:
        groups = cached[1]
    else:
        rows = (
            await db.execute(
                select(
                    HoldoutGroup.key,
                    HoldoutGroup.holdout_bp,
                    HoldoutGroup.scope_org_id,
                    HoldoutGroup.ends_at,
                ).where(HoldoutGroup.domain == domain, HoldoutGroup.status == "active")
            )
        ).all()
        groups = [tuple(row) for row in rows]
        _GROUP_CACHE[domain] = (now_mono + _GROUP_CACHE_TTL_SECONDS, groups)
    now = datetime.now(UTC)
    return [g for g in groups if g[3] is None or g[3] > now]


class HoldoutGroupService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        key: str,
        title: str,
        domain: str,
        holdout_bp: int,
        scope_org_id: str | None = None,
        ends_at: datetime | None = None,
        actor_id: str | None = None,
    ) -> HoldoutGroup:
        if domain not in EXPERIMENT_DOMAINS:
            raise AppError("EXPERIMENT_DOMAIN_INVALID", f"Unknown domain: {domain}", 422)
        if not 1 <= holdout_bp <= HOLDOUT_GROUP_MAX_BP:
            raise AppError(
                "EXPERIMENT_HOLDOUT_BP_INVALID",
                f"holdout_bp must be in [1, {HOLDOUT_GROUP_MAX_BP}]",
                422,
            )
        if scope_org_id is not None:
            org = await self.db.get(Organization, scope_org_id)
            if org is None:
                # uniform 404 — no org-existence oracle (R89 class)
                raise AppError("ORG_NOT_FOUND", "Organization not found", 404)
        taken = (
            await self.db.execute(
                select(HoldoutGroup.id).where(
                    HoldoutGroup.key == key, HoldoutGroup.status == "active"
                )
            )
        ).scalar_one_or_none()
        if taken is not None:
            raise AppError("EXPERIMENT_HOLDOUT_KEY_TAKEN", "Holdout group key already exists", 409)
        group = HoldoutGroup(
            key=key,
            title=title,
            domain=domain,
            holdout_bp=holdout_bp,
            scope_org_id=scope_org_id,
            ends_at=ends_at,
            created_by=actor_id,
        )
        self.db.add(group)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            # Defect #33 (R88 class): the pre-check select has a race window —
            # a concurrent create of the same key must land as the SAME typed
            # 409, never an unmapped 500
            raise AppError(
                "EXPERIMENT_HOLDOUT_KEY_TAKEN", "Holdout group key already exists", 409
            ) from exc
        invalidate_holdout_group_cache()
        return group

    async def list_groups(self) -> list[HoldoutGroup]:
        return list(
            (
                await self.db.execute(
                    select(HoldoutGroup).order_by(HoldoutGroup.created_at.desc())
                )
            ).scalars()
        )

    async def release(self, group_id: str) -> HoldoutGroup:
        group = await self.db.get(HoldoutGroup, group_id)
        if group is None:
            raise AppError("EXPERIMENT_HOLDOUT_NOT_FOUND", "Holdout group not found", 404)
        if group.status == "released":
            return group  # idempotent
        group.status = "released"
        if group.ends_at is None:
            group.ends_at = datetime.now(UTC)
        await self.db.flush()
        invalidate_holdout_group_cache()
        return group
