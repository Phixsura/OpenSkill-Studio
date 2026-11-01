"""AI System Inventory service (ADR-017 Part A).

Module-level functions, db: AsyncSession first arg, no db.commit().
"""

from __future__ import annotations

import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.inventory import (
    VALID_TRANSITIONS,
    AISystem,
    AISystemUseCase,
    SystemLifecycle,
    SystemType,
    UseType,
)
from app.trustplane.services.audit import record_trust_audit

# ── Errors ───────────────────────────────────────────────────────────


class SystemNotFoundError(AppError):
    def __init__(self):
        super().__init__("SYSTEM_NOT_FOUND", "AI system not found", 404)


class SystemSlugConflictError(AppError):
    def __init__(self, slug: str):
        super().__init__("SYSTEM_SLUG_CONFLICT", f"Slug '{slug}' already exists in this org", 409)


class SystemInvalidTransitionError(AppError):
    def __init__(self, current: str, target: str):
        super().__init__(
            "SYSTEM_INVALID_TRANSITION",
            f"Cannot transition from '{current}' to '{target}'",
            422,
        )


class SystemDeployedUseCaseDeleteError(AppError):
    def __init__(self):
        super().__init__(
            "SYSTEM_DEPLOYED_USE_CASE_DELETE",
            "Cannot delete use cases from a deployed or monitored system",
            422,
        )


class UseCaseNotFoundError(AppError):
    def __init__(self):
        super().__init__("USE_CASE_NOT_FOUND", "Use case not found", 404)


# ── Slug generation ──────────────────────────────────────────────────

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(name: str) -> str:
    return _SLUG_RE.sub("-", name.lower()).strip("-")[:100]


# ── System CRUD ──────────────────────────────────────────────────────


async def create_system(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    name: str,
    system_type: str,
    slug: str | None = None,
    description: str | None = None,
    linked_entity_type: str | None = None,
    linked_entity_id: str | None = None,
    tags: list | None = None,
    metadata_: dict | None = None,
) -> AISystem:
    slug = slug or _slugify(name)

    # Check slug uniqueness within org
    existing = await db.execute(
        select(AISystem.id).where(AISystem.org_id == org_id, AISystem.slug == slug)
    )
    if existing.scalar_one_or_none() is not None:
        raise SystemSlugConflictError(slug)

    system = AISystem(
        org_id=org_id,
        name=name,
        slug=slug,
        description=description,
        system_type=SystemType(system_type),
        lifecycle=SystemLifecycle.DRAFT,
        owner_user_id=user_id,
        linked_entity_type=linked_entity_type,
        linked_entity_id=linked_entity_id,
        tags=tags or [],
        metadata_=metadata_ or {},
    )
    db.add(system)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="system.created",
        target_type="ai_system",
        target_id=system.id,
        after={"name": name, "slug": slug, "system_type": system_type},
    )
    return system


async def get_system(db: AsyncSession, system_id: str, org_id: str) -> AISystem:
    result = await db.execute(
        select(AISystem).where(AISystem.id == system_id, AISystem.org_id == org_id)
    )
    system = result.scalar_one_or_none()
    if system is None:
        raise SystemNotFoundError()
    return system


async def list_systems(
    db: AsyncSession,
    org_id: str,
    *,
    lifecycle: str | None = None,
    system_type: str | None = None,
    risk_tier: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[AISystem], int]:
    base = select(AISystem).where(AISystem.org_id == org_id)
    count_base = select(func.count()).select_from(AISystem).where(AISystem.org_id == org_id)

    if lifecycle:
        base = base.where(AISystem.lifecycle == lifecycle)
        count_base = count_base.where(AISystem.lifecycle == lifecycle)
    if system_type:
        base = base.where(AISystem.system_type == system_type)
        count_base = count_base.where(AISystem.system_type == system_type)
    if risk_tier:
        base = base.where(AISystem.risk_tier == risk_tier)
        count_base = count_base.where(AISystem.risk_tier == risk_tier)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(AISystem.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


async def update_system(
    db: AsyncSession,
    system_id: str,
    org_id: str,
    user_id: str,
    **fields,
) -> AISystem:
    system = await get_system(db, system_id, org_id)
    before = {}
    after = {}

    # Material fields that bump version
    material = {"name", "description", "system_type"}
    bump = False

    for key, value in fields.items():
        if value is not None and hasattr(system, key):
            old = getattr(system, key)
            if isinstance(old, SystemType):
                old = old.value
            before[key] = old
            if key == "system_type":
                value = SystemType(value)
            setattr(system, key, value)
            after[key] = value if not isinstance(value, SystemType) else value.value
            if key in material:
                bump = True

    if bump:
        system.version += 1
        after["version"] = system.version

    await db.flush()
    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="system.updated",
        target_type="ai_system",
        target_id=system_id,
        before=before,
        after=after,
    )
    return system


async def change_lifecycle(
    db: AsyncSession,
    system_id: str,
    org_id: str,
    user_id: str,
    new_lifecycle: str,
    reason: str | None = None,
) -> AISystem:
    system = await get_system(db, system_id, org_id)
    target = SystemLifecycle(new_lifecycle)
    allowed = VALID_TRANSITIONS.get(system.lifecycle, set())
    if target not in allowed:
        raise SystemInvalidTransitionError(system.lifecycle.value, target.value)

    old = system.lifecycle.value
    system.lifecycle = target
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="system.lifecycle_changed",
        target_type="ai_system",
        target_id=system_id,
        before={"lifecycle": old},
        after={"lifecycle": target.value},
        reason=reason,
    )
    return system


async def link_entity(
    db: AsyncSession,
    system_id: str,
    org_id: str,
    user_id: str,
    entity_type: str,
    entity_id: str,
) -> AISystem:
    system = await get_system(db, system_id, org_id)
    before = {
        "linked_entity_type": system.linked_entity_type,
        "linked_entity_id": system.linked_entity_id,
    }
    system.linked_entity_type = entity_type
    system.linked_entity_id = entity_id
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="system.linked",
        target_type="ai_system",
        target_id=system_id,
        before=before,
        after={"linked_entity_type": entity_type, "linked_entity_id": entity_id},
    )
    return system


# ── Use Case CRUD ────────────────────────────────────────────────────


async def create_use_case(
    db: AsyncSession,
    system_id: str,
    org_id: str,
    user_id: str,
    *,
    use_type: str,
    title: str,
    description: str,
    affected_groups: list | None = None,
    data_classes: list | None = None,
    deployment_contexts: list | None = None,
    regions: list | None = None,
) -> AISystemUseCase:
    # Validate system belongs to org
    await get_system(db, system_id, org_id)

    use_case = AISystemUseCase(
        system_id=system_id,
        use_type=UseType(use_type),
        title=title,
        description=description,
        affected_groups=affected_groups or [],
        data_classes=data_classes or [],
        deployment_contexts=deployment_contexts or [],
        regions=regions or [],
        created_by=user_id,
    )
    db.add(use_case)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="use_case.created",
        target_type="ai_system_use_case",
        target_id=use_case.id,
        after={"system_id": system_id, "use_type": use_type, "title": title},
    )
    return use_case


async def list_use_cases(
    db: AsyncSession,
    system_id: str,
    org_id: str,
) -> list[AISystemUseCase]:
    # Validate system belongs to org
    await get_system(db, system_id, org_id)

    result = await db.execute(
        select(AISystemUseCase)
        .where(AISystemUseCase.system_id == system_id)
        .order_by(AISystemUseCase.created_at)
    )
    return list(result.scalars().all())


async def update_use_case(
    db: AsyncSession,
    use_id: str,
    system_id: str,
    org_id: str,
    user_id: str,
    **fields,
) -> AISystemUseCase:
    # Validate system belongs to org
    await get_system(db, system_id, org_id)

    result = await db.execute(
        select(AISystemUseCase).where(
            AISystemUseCase.id == use_id, AISystemUseCase.system_id == system_id
        )
    )
    use_case = result.scalar_one_or_none()
    if use_case is None:
        raise UseCaseNotFoundError()

    before = {}
    after = {}
    for key, value in fields.items():
        if value is not None and hasattr(use_case, key):
            before[key] = getattr(use_case, key)
            setattr(use_case, key, value)
            after[key] = value

    await db.flush()
    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="use_case.updated",
        target_type="ai_system_use_case",
        target_id=use_id,
        before=before,
        after=after,
    )
    return use_case


async def delete_use_case(
    db: AsyncSession,
    use_id: str,
    system_id: str,
    org_id: str,
    user_id: str,
) -> None:
    system = await get_system(db, system_id, org_id)

    # Cannot remove intended uses from live systems
    if system.lifecycle in (SystemLifecycle.DEPLOYED, SystemLifecycle.MONITORING):
        raise SystemDeployedUseCaseDeleteError()

    result = await db.execute(
        select(AISystemUseCase).where(
            AISystemUseCase.id == use_id, AISystemUseCase.system_id == system_id
        )
    )
    use_case = result.scalar_one_or_none()
    if use_case is None:
        raise UseCaseNotFoundError()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="use_case.deleted",
        target_type="ai_system_use_case",
        target_id=use_id,
        before={"title": use_case.title, "use_type": use_case.use_type.value},
    )
    await db.delete(use_case)
    await db.flush()
