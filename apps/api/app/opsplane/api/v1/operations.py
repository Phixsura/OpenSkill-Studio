"""Global Operations API (Issue #46).

Platform-scoped endpoints for infrastructure, reliability, and governance.
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.models.user import User, UserRole
from app.opsplane.services import governance as gov_svc
from app.opsplane.services import infrastructure as infra_svc
from app.opsplane.services import reliability as rel_svc
from app.schemas.base import DataResponse, ListResponse, PaginationMeta

router = APIRouter(tags=["Operations"])


def _require_platform_admin(user: User) -> None:
    from fastapi import HTTPException
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Platform admin required")


# ── Response models (from_attributes) ────────────────────────────────

class RegionResponse(BaseModel):
    id: str
    code: str
    name: str
    provider: str
    status: str
    is_primary: bool
    created_at: str
    model_config = {"from_attributes": True}

class CellResponse(BaseModel):
    id: str
    region_id: str
    name: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}

class ServiceResponse(BaseModel):
    id: str
    cell_id: str
    service_name: str
    version: str
    status: str
    endpoint: str | None
    created_at: str
    model_config = {"from_attributes": True}

class SloResponse(BaseModel):
    id: str
    name: str
    sli_metric: str
    target_value: str
    target_unit: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}

class OpsIncidentResponse(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    region_id: str | None
    detection_source: str
    detected_at: str
    created_at: str
    model_config = {"from_attributes": True}

class DetectionRuleResponse(BaseModel):
    id: str
    name: str
    rule_type: str
    severity: str
    status: str
    cooldown_minutes: int
    created_at: str
    model_config = {"from_attributes": True}

class FailoverResponse(BaseModel):
    id: str
    source_region_id: str
    target_region_id: str
    trigger: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}

class RecoveryPlanResponse(BaseModel):
    id: str
    name: str
    scenario: str
    status: str
    rto_minutes: int | None
    rpo_minutes: int | None
    created_at: str
    model_config = {"from_attributes": True}

class PolicyResponse(BaseModel):
    id: str
    name: str
    policy_type: str
    status: str
    enforcement_mode: str
    version: int
    created_at: str
    model_config = {"from_attributes": True}

class PlaybookResponse(BaseModel):
    id: str
    name: str
    status: str
    requires_approval: bool
    created_at: str
    model_config = {"from_attributes": True}

class BudgetResponse(BaseModel):
    id: str
    name: str
    budget_minor: int
    currency: str
    period: str
    current_spend_minor: int
    is_active: bool
    created_at: str
    model_config = {"from_attributes": True}

class GameDayResponse(BaseModel):
    id: str
    name: str
    scenario: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}

class HealingResponse(BaseModel):
    id: str
    action_type: str
    description: str
    status: str
    requires_human_approval: bool
    created_at: str
    model_config = {"from_attributes": True}

class ComplianceResponse(BaseModel):
    id: str
    framework: str
    control_id: str
    title: str
    status: str
    created_at: str
    model_config = {"from_attributes": True}


# ── Request models ───────────────────────────────────────────────────

class CreateRegionRequest(BaseModel):
    code: str
    name: str
    provider: str
    is_primary: bool = False
    config: dict | None = None

class CreateCellRequest(BaseModel):
    region_id: str
    name: str
    capacity: dict | None = None

class RegisterServiceRequest(BaseModel):
    cell_id: str
    service_name: str
    version: str
    endpoint: str | None = None

class CreateSloRequest(BaseModel):
    name: str
    sli_metric: str
    target_value: str
    target_unit: str
    error_budget_total: str
    org_id: str | None = None
    description: str | None = None

class CreateIncidentRequest(BaseModel):
    title: str
    severity: str
    description: str | None = None
    region_id: str | None = None
    detection_source: str = "manual"

class CreateDetectionRuleRequest(BaseModel):
    name: str
    rule_type: str
    conditions: dict
    severity: str
    description: str | None = None

class CreateFailoverRequest(BaseModel):
    source_region_id: str
    target_region_id: str
    trigger: str
    incident_id: str | None = None

class CreateRecoveryPlanRequest(BaseModel):
    name: str
    scenario: str
    steps: list
    description: str | None = None
    rto_minutes: int | None = None
    rpo_minutes: int | None = None

class CreatePolicyRequest(BaseModel):
    name: str
    policy_type: str
    rules: dict
    description: str | None = None
    enforcement_mode: str = "enforce"

class CreatePlaybookRequest(BaseModel):
    name: str
    trigger_conditions: dict
    steps: list
    description: str | None = None
    rollback_steps: list | None = None
    requires_approval: bool = True

class CreateBudgetRequest(BaseModel):
    name: str
    budget_minor: int
    currency: str = "USD"
    period: str = "monthly"
    tenant_id: str | None = None

class CreateGameDayRequest(BaseModel):
    name: str
    scenario: str
    plan: dict
    description: str | None = None
    participants: list | None = None
    scheduled_at: str | None = None

class ProposeHealingRequest(BaseModel):
    action_type: str
    description: str
    incident_id: str | None = None
    playbook_id: str | None = None
    blast_radius: dict | None = None

class CollectEvidenceRequest(BaseModel):
    framework: str
    control_id: str
    title: str
    evidence_data: dict
    expires_at: str | None = None


# ── Infrastructure (Parts A, B, D) ───────────────────────────────────

@router.post("/platform/ops/regions", response_model=DataResponse[RegionResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_region(body: CreateRegionRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    region = await infra_svc.create_region(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=RegionResponse.model_validate(region))

@router.get("/platform/ops/regions", response_model=DataResponse[list[RegionResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_regions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    regions = await infra_svc.list_regions(db)
    return DataResponse(data=[RegionResponse.model_validate(r) for r in regions])

@router.post("/platform/ops/cells", response_model=DataResponse[CellResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_cell(body: CreateCellRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    cell = await infra_svc.create_cell(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=CellResponse.model_validate(cell))

@router.get("/platform/ops/cells", response_model=DataResponse[list[CellResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_cells(region_id: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    cells = await infra_svc.list_cells(db, region_id=region_id)
    return DataResponse(data=[CellResponse.model_validate(c) for c in cells])

@router.post("/platform/ops/services", response_model=DataResponse[ServiceResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def register_service(body: RegisterServiceRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    svc = await infra_svc.register_service(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ServiceResponse.model_validate(svc))

@router.get("/platform/ops/services", response_model=DataResponse[list[ServiceResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_services(cell_id: str | None = None, service_name: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    services = await infra_svc.list_services(db, cell_id=cell_id, service_name=service_name)
    return DataResponse(data=[ServiceResponse.model_validate(s) for s in services])

# ── Reliability (Parts C, E, F, I, L) ────────────────────────────────

@router.post("/platform/ops/slos", response_model=DataResponse[SloResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_slo(body: CreateSloRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    slo = await rel_svc.create_slo(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=SloResponse.model_validate(slo))

@router.get("/platform/ops/slos", response_model=DataResponse[list[SloResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_slos(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    slos = await rel_svc.list_slos(db)
    return DataResponse(data=[SloResponse.model_validate(s) for s in slos])

@router.post("/platform/ops/incidents", response_model=DataResponse[OpsIncidentResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_incident(body: CreateIncidentRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    incident = await rel_svc.create_incident(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=OpsIncidentResponse.model_validate(incident))

@router.get("/platform/ops/incidents", response_model=ListResponse[OpsIncidentResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_incidents(severity: str | None = None, status: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    incidents, total = await rel_svc.list_incidents(db, severity=severity, status=status, page=page, per_page=per_page)
    return ListResponse(data=[OpsIncidentResponse.model_validate(i) for i in incidents], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))

@router.post("/platform/ops/detection-rules", response_model=DataResponse[DetectionRuleResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_detection_rule(body: CreateDetectionRuleRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    rule = await rel_svc.create_detection_rule(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=DetectionRuleResponse.model_validate(rule))

@router.get("/platform/ops/detection-rules", response_model=DataResponse[list[DetectionRuleResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_detection_rules(status: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    rules = await rel_svc.list_detection_rules(db, status=status)
    return DataResponse(data=[DetectionRuleResponse.model_validate(r) for r in rules])

@router.post("/platform/ops/failovers", response_model=DataResponse[FailoverResponse], status_code=201, dependencies=[Depends(rate_limit(5, 60))])
async def create_failover(body: CreateFailoverRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    record = await rel_svc.create_failover(db, initiated_by=user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=FailoverResponse.model_validate(record))

@router.get("/platform/ops/failovers", response_model=ListResponse[FailoverResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_failovers(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    records, total = await rel_svc.list_failovers(db, page=page, per_page=per_page)
    return ListResponse(data=[FailoverResponse.model_validate(r) for r in records], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))

@router.post("/platform/ops/recovery-plans", response_model=DataResponse[RecoveryPlanResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_recovery_plan(body: CreateRecoveryPlanRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    plan = await rel_svc.create_recovery_plan(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=RecoveryPlanResponse.model_validate(plan))

@router.get("/platform/ops/recovery-plans", response_model=DataResponse[list[RecoveryPlanResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_recovery_plans(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    plans = await rel_svc.list_recovery_plans(db)
    return DataResponse(data=[RecoveryPlanResponse.model_validate(p) for p in plans])

# ── Governance (Parts G, H, J, K, M, N, O, P, R, S) ─────────────────

@router.post("/platform/ops/policies", response_model=DataResponse[PolicyResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_policy(body: CreatePolicyRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    policy = await gov_svc.create_policy(db, created_by=user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=PolicyResponse.model_validate(policy))

@router.get("/platform/ops/policies", response_model=DataResponse[list[PolicyResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_policies(policy_type: str | None = None, status: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    policies = await gov_svc.list_policies(db, policy_type=policy_type, status=status)
    return DataResponse(data=[PolicyResponse.model_validate(p) for p in policies])

@router.post("/platform/ops/playbooks", response_model=DataResponse[PlaybookResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_playbook(body: CreatePlaybookRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    pb = await gov_svc.create_playbook(db, created_by=user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=PlaybookResponse.model_validate(pb))

@router.get("/platform/ops/playbooks", response_model=DataResponse[list[PlaybookResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_playbooks(status: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    playbooks = await gov_svc.list_playbooks(db, status=status)
    return DataResponse(data=[PlaybookResponse.model_validate(p) for p in playbooks])

@router.post("/platform/ops/budgets", response_model=DataResponse[BudgetResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_budget(body: CreateBudgetRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    budget = await gov_svc.create_budget(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=BudgetResponse.model_validate(budget))

@router.get("/platform/ops/budgets", response_model=DataResponse[list[BudgetResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_budgets(tenant_id: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    budgets = await gov_svc.list_budgets(db, tenant_id=tenant_id)
    return DataResponse(data=[BudgetResponse.model_validate(b) for b in budgets])

@router.post("/platform/ops/game-days", response_model=DataResponse[GameDayResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_game_day(body: CreateGameDayRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    gd = await gov_svc.create_game_day(db, created_by=user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=GameDayResponse.model_validate(gd))

@router.get("/platform/ops/game-days", response_model=DataResponse[list[GameDayResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_game_days(status: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    gds = await gov_svc.list_game_days(db, status=status)
    return DataResponse(data=[GameDayResponse.model_validate(g) for g in gds])

@router.post("/platform/ops/healing", response_model=DataResponse[HealingResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def propose_healing(body: ProposeHealingRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    action = await gov_svc.propose_healing(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=HealingResponse.model_validate(action))

@router.post("/platform/ops/healing/{action_id}/approve", response_model=DataResponse[HealingResponse], dependencies=[Depends(rate_limit(10, 60))])
async def approve_healing(action_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    action = await gov_svc.approve_healing(db, action_id, approved_by=user.id)
    await db.commit()
    return DataResponse(data=HealingResponse.model_validate(action))

@router.get("/platform/ops/healing", response_model=DataResponse[list[HealingResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_healing(status: str | None = None, incident_id: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    actions = await gov_svc.list_healing_actions(db, status=status, incident_id=incident_id)
    return DataResponse(data=[HealingResponse.model_validate(a) for a in actions])

@router.post("/platform/ops/compliance", response_model=DataResponse[ComplianceResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def collect_evidence(body: CollectEvidenceRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    ev = await gov_svc.collect_evidence(db, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ComplianceResponse.model_validate(ev))

@router.get("/platform/ops/compliance", response_model=DataResponse[list[ComplianceResponse]], dependencies=[Depends(rate_limit(30, 60))])
async def list_compliance(framework: str | None = None, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_platform_admin(user)
    evidence = await gov_svc.list_compliance_evidence(db, framework=framework)
    return DataResponse(data=[ComplianceResponse.model_validate(e) for e in evidence])
