"""Governance service (Issue #46 Parts G, H, J, K, M, N, O, P, R, S)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.opsplane.models.governance import (
    ComplianceEvidence,
    CostBudget,
    CostCategory,
    CostRecord,
    GameDay,
    HealingAction,
    HealingActionStatus,
    OpsPolicy,
    PlaybookRun,
    RemediationPlaybook,
)


class PolicyNotFoundError(AppError):
    def __init__(self):
        super().__init__("OPS_POLICY_NOT_FOUND", "Operations policy not found", 404)


class PlaybookNotFoundError(AppError):
    def __init__(self):
        super().__init__("PLAYBOOK_NOT_FOUND", "Remediation playbook not found", 404)


# ── Policies ─────────────────────────────────────────────────────────


async def create_policy(db: AsyncSession, *, name: str, policy_type: str, rules: dict, description: str | None = None, enforcement_mode: str = "enforce", scope: dict | None = None, created_by: str | None = None) -> OpsPolicy:
    policy = OpsPolicy(name=name, description=description, policy_type=policy_type, rules=rules, enforcement_mode=enforcement_mode, scope=scope or {}, created_by=created_by)
    db.add(policy)
    await db.flush()
    return policy


async def list_policies(db: AsyncSession, policy_type: str | None = None, status: str | None = None) -> list[OpsPolicy]:
    base = select(OpsPolicy)
    if policy_type:
        base = base.where(OpsPolicy.policy_type == policy_type)
    if status:
        base = base.where(OpsPolicy.status == status)
    result = await db.execute(base.order_by(OpsPolicy.name))
    return list(result.scalars().all())


# ── Playbooks ────────────────────────────────────────────────────────


async def create_playbook(db: AsyncSession, *, name: str, trigger_conditions: dict, steps: list, description: str | None = None, rollback_steps: list | None = None, requires_approval: bool = True, created_by: str | None = None) -> RemediationPlaybook:
    playbook = RemediationPlaybook(
        name=name, description=description, trigger_conditions=trigger_conditions,
        steps=steps, rollback_steps=rollback_steps or [],
        requires_approval=requires_approval, created_by=created_by,
    )
    db.add(playbook)
    await db.flush()
    return playbook


async def list_playbooks(db: AsyncSession, status: str | None = None) -> list[RemediationPlaybook]:
    base = select(RemediationPlaybook)
    if status:
        base = base.where(RemediationPlaybook.status == status)
    result = await db.execute(base.order_by(RemediationPlaybook.name))
    return list(result.scalars().all())


async def run_playbook(db: AsyncSession, playbook_id: str, incident_id: str | None = None) -> PlaybookRun:
    run = PlaybookRun(playbook_id=playbook_id, incident_id=incident_id)
    db.add(run)
    await db.flush()
    return run


# ── FinOps ───────────────────────────────────────────────────────────


async def record_cost(db: AsyncSession, *, category: str, provider: str, service_name: str, amount_minor: int, currency: str, quantity: str, unit: str, period_start: str, period_end: str, tenant_id: str | None = None, region_id: str | None = None, tags: dict | None = None) -> CostRecord:
    record = CostRecord(
        tenant_id=tenant_id, category=CostCategory(category), provider=provider,
        service_name=service_name, region_id=region_id, amount_minor=amount_minor,
        currency=currency, quantity=Decimal(quantity), unit=unit,
        period_start=datetime.fromisoformat(period_start),
        period_end=datetime.fromisoformat(period_end), tags=tags or {},
    )
    db.add(record)
    await db.flush()
    return record


async def create_budget(db: AsyncSession, *, name: str, budget_minor: int, currency: str = "USD", period: str = "monthly", tenant_id: str | None = None, category: str | None = None) -> CostBudget:
    budget = CostBudget(name=name, tenant_id=tenant_id, category=category, budget_minor=budget_minor, currency=currency, period=period)
    db.add(budget)
    await db.flush()
    return budget


async def list_budgets(db: AsyncSession, tenant_id: str | None = None) -> list[CostBudget]:
    base = select(CostBudget).where(CostBudget.is_active.is_(True))
    if tenant_id:
        base = base.where(CostBudget.tenant_id == tenant_id)
    result = await db.execute(base.order_by(CostBudget.name))
    return list(result.scalars().all())


# ── Game Days ────────────────────────────────────────────────────────


async def create_game_day(db: AsyncSession, *, name: str, scenario: str, plan: dict, description: str | None = None, participants: list | None = None, scheduled_at: str | None = None, created_by: str | None = None) -> GameDay:
    gd = GameDay(
        name=name, description=description, scenario=scenario, plan=plan,
        participants=participants or [],
        scheduled_at=datetime.fromisoformat(scheduled_at) if scheduled_at else None,
        created_by=created_by,
    )
    db.add(gd)
    await db.flush()
    return gd


async def list_game_days(db: AsyncSession, status: str | None = None) -> list[GameDay]:
    base = select(GameDay)
    if status:
        base = base.where(GameDay.status == status)
    result = await db.execute(base.order_by(GameDay.created_at.desc()))
    return list(result.scalars().all())


# ── Healing Actions ──────────────────────────────────────────────────


async def propose_healing(db: AsyncSession, *, action_type: str, description: str, incident_id: str | None = None, playbook_id: str | None = None, blast_radius: dict | None = None, requires_human_approval: bool = True) -> HealingAction:
    action = HealingAction(
        incident_id=incident_id, playbook_id=playbook_id, action_type=action_type,
        description=description, blast_radius=blast_radius,
        requires_human_approval=requires_human_approval,
    )
    db.add(action)
    await db.flush()
    return action


async def approve_healing(db: AsyncSession, action_id: str, approved_by: str) -> HealingAction:
    action = await db.get(HealingAction, action_id)
    if action is None:
        raise AppError("HEALING_NOT_FOUND", "Healing action not found", 404)
    action.status = HealingActionStatus.APPROVED
    action.approved_by = approved_by
    await db.flush()
    return action


async def list_healing_actions(db: AsyncSession, status: str | None = None, incident_id: str | None = None) -> list[HealingAction]:
    base = select(HealingAction)
    if status:
        base = base.where(HealingAction.status == status)
    if incident_id:
        base = base.where(HealingAction.incident_id == incident_id)
    result = await db.execute(base.order_by(HealingAction.created_at.desc()))
    return list(result.scalars().all())


# ── Compliance ───────────────────────────────────────────────────────


async def collect_evidence(db: AsyncSession, *, framework: str, control_id: str, title: str, evidence_data: dict, expires_at: str | None = None) -> ComplianceEvidence:
    ev = ComplianceEvidence(
        framework=framework, control_id=control_id, title=title,
        evidence_data=evidence_data,
        expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
    )
    db.add(ev)
    await db.flush()
    return ev


async def list_compliance_evidence(db: AsyncSession, framework: str | None = None) -> list[ComplianceEvidence]:
    base = select(ComplianceEvidence)
    if framework:
        base = base.where(ComplianceEvidence.framework == framework)
    result = await db.execute(base.order_by(ComplianceEvidence.collected_at.desc()))
    return list(result.scalars().all())
