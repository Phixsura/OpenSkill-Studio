"""Threat Modeling & Red-Team service (ADR-017 Part E)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.inventory import AISystem
from app.trustplane.models.threats import (
    RedTeamFinding,
    RedTeamRun,
    RedTeamSuite,
    TestRunStatus,
    ThreatCategory,
    ThreatModel,
    ThreatSeverity,
)
from app.trustplane.services.audit import record_trust_audit
from app.trustplane.services.inventory import SystemNotFoundError


class ThreatNotFoundError(AppError):
    def __init__(self):
        super().__init__("THREAT_NOT_FOUND", "Threat model not found", 404)


class SuiteNotFoundError(AppError):
    def __init__(self):
        super().__init__("SUITE_NOT_FOUND", "Red-team suite not found", 404)


class RunNotFoundError(AppError):
    def __init__(self):
        super().__init__("RUN_NOT_FOUND", "Red-team run not found", 404)


# ── Threat Models ────────────────────────────────────────────────────


async def create_threat_model(
    db: AsyncSession, org_id: str, user_id: str, **data
) -> ThreatModel:
    system_id = data.pop("system_id", None)
    if system_id:
        r = await db.execute(select(AISystem.id).where(AISystem.id == system_id, AISystem.org_id == org_id))
        if r.scalar_one_or_none() is None:
            raise SystemNotFoundError()

    model = ThreatModel(
        org_id=org_id,
        system_id=system_id,
        name=data["name"],
        description=data.get("description"),
        category=ThreatCategory(data["category"]),
        severity=ThreatSeverity(data.get("severity", "medium")),
        attack_vectors=data.get("attack_vectors", []),
        preconditions=data.get("preconditions", []),
        mitigations=data.get("mitigations", []),
        affected_components=data.get("affected_components", []),
        created_by=user_id,
    )
    db.add(model)
    await db.flush()

    await record_trust_audit(
        db, org_id=org_id, actor_user_id=user_id, actor_type="user",
        action="threat.created", target_type="threat_model", target_id=model.id,
        after={"name": data["name"], "category": data["category"]},
    )
    return model


async def list_threat_models(
    db: AsyncSession, org_id: str, *, category: str | None = None, page: int = 1, per_page: int = 20,
) -> tuple[list[ThreatModel], int]:
    base = select(ThreatModel).where(ThreatModel.org_id == org_id)
    count_q = select(func.count()).select_from(ThreatModel).where(ThreatModel.org_id == org_id)
    if category:
        base = base.where(ThreatModel.category == category)
        count_q = count_q.where(ThreatModel.category == category)
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(base.order_by(ThreatModel.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    return list(result.scalars().all()), total


async def get_threat_model(db: AsyncSession, threat_id: str, org_id: str) -> ThreatModel:
    result = await db.execute(select(ThreatModel).where(ThreatModel.id == threat_id, ThreatModel.org_id == org_id))
    m = result.scalar_one_or_none()
    if m is None:
        raise ThreatNotFoundError()
    return m


# ── Red-Team Suites ──────────────────────────────────────────────────


async def create_suite(
    db: AsyncSession, org_id: str, user_id: str, **data
) -> RedTeamSuite:
    # Validate threat_model_id belongs to org (IDOR guard)
    if data.get("threat_model_id"):
        await get_threat_model(db, data["threat_model_id"], org_id)

    suite = RedTeamSuite(
        org_id=org_id,
        threat_model_id=data.get("threat_model_id"),
        name=data["name"],
        description=data.get("description"),
        fixtures=data.get("fixtures", []),
        isolation_config=data.get("isolation_config", {}),
        test_count=len(data.get("fixtures", [])),
        created_by=user_id,
    )
    db.add(suite)
    await db.flush()

    await record_trust_audit(
        db, org_id=org_id, actor_user_id=user_id, actor_type="user",
        action="suite.created", target_type="redteam_suite", target_id=suite.id,
        after={"name": data["name"]},
    )
    return suite


async def list_suites(
    db: AsyncSession, org_id: str, *, page: int = 1, per_page: int = 20,
) -> tuple[list[RedTeamSuite], int]:
    base = select(RedTeamSuite).where(RedTeamSuite.org_id == org_id)
    count_q = select(func.count()).select_from(RedTeamSuite).where(RedTeamSuite.org_id == org_id)
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(base.order_by(RedTeamSuite.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    return list(result.scalars().all()), total


async def get_suite(db: AsyncSession, suite_id: str, org_id: str) -> RedTeamSuite:
    result = await db.execute(select(RedTeamSuite).where(RedTeamSuite.id == suite_id, RedTeamSuite.org_id == org_id))
    s = result.scalar_one_or_none()
    if s is None:
        raise SuiteNotFoundError()
    return s


# ── Red-Team Runs ────────────────────────────────────────────────────


async def start_run(
    db: AsyncSession, org_id: str, user_id: str, suite_id: str, system_id: str | None = None,
) -> RedTeamRun:
    await get_suite(db, suite_id, org_id)
    # Validate system_id belongs to org (IDOR guard)
    if system_id:
        r = await db.execute(select(AISystem.id).where(AISystem.id == system_id, AISystem.org_id == org_id))
        if r.scalar_one_or_none() is None:
            raise SystemNotFoundError()
    run = RedTeamRun(
        org_id=org_id, suite_id=suite_id, system_id=system_id,
        status=TestRunStatus.PENDING, started_by=user_id,
    )
    db.add(run)
    await db.flush()

    await record_trust_audit(
        db, org_id=org_id, actor_user_id=user_id, actor_type="user",
        action="run.started", target_type="redteam_run", target_id=run.id,
        after={"suite_id": suite_id},
    )
    return run


async def list_runs(
    db: AsyncSession, org_id: str, *, suite_id: str | None = None, page: int = 1, per_page: int = 20,
) -> tuple[list[RedTeamRun], int]:
    base = select(RedTeamRun).where(RedTeamRun.org_id == org_id)
    count_q = select(func.count()).select_from(RedTeamRun).where(RedTeamRun.org_id == org_id)
    if suite_id:
        base = base.where(RedTeamRun.suite_id == suite_id)
        count_q = count_q.where(RedTeamRun.suite_id == suite_id)
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(base.order_by(RedTeamRun.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    return list(result.scalars().all()), total


async def list_findings(
    db: AsyncSession, run_id: str, org_id: str,
) -> list[RedTeamFinding]:
    # Validate run belongs to org (IDOR guard)
    r = await db.execute(
        select(RedTeamRun.id).where(RedTeamRun.id == run_id, RedTeamRun.org_id == org_id)
    )
    if r.scalar_one_or_none() is None:
        raise RunNotFoundError()
    result = await db.execute(
        select(RedTeamFinding).where(RedTeamFinding.run_id == run_id).order_by(RedTeamFinding.created_at)
    )
    return list(result.scalars().all())
