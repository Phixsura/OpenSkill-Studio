"""Decision registry & promotion DB tests (ADR-017 exp06).

Decide-references-analysis (hash gate), terminal uniqueness, extend semantics,
observational promote refusal, target whitelist (employment structurally
absent), draft→approve→apply lifecycle with idempotency, the two real apply
adapters (inactive MatchingConfig version, draft LearningPath), unwired-target
refusal, LIKE-escaped registry search, and corpus meta.

Runs against the dev Postgres (exp05 applied); rollback-per-test.
"""

from datetime import UTC, datetime, time, timedelta

import pytest
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.exceptions import AppError
from app.experiments.security import ETHICS_CHECKLIST_KEY, LAUNCH_CHECKLIST_KEYS
from app.experiments.services.analysis_service import AnalysisService
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.decisions import DecisionService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.layers import LayerService
from app.experiments.services.metrics import MetricService
from app.experiments.services.promotion import PromotionService
from app.models.matching import MatchingConfig
from app.models.user import User, UserRole, UserStatus

_CHECKLIST = {key: True for key in (*LAUNCH_CHECKLIST_KEYS, ETHICS_CHECKLIST_KEY)}

@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def _spec(**overrides) -> dict:
    base = {
        "hypothesis": "decision registry gates promotion correctly and safely",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 5000},
        ],
        "metrics": {
            "primary": ["exposure_rate"],
            "guardrails": [{"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}],
        },
    }
    base.update(overrides)
    return base


async def _mk_admin(db) -> User:
    user = User(
        email=f"exp-dec-{ULID()}@example.com",
        display_name="D",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_analyzed(db, **spec_overrides):
    """Full pipeline to `analyzed` with one recorded analysis run."""
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    await svc.create_version(exp.id, spec=_spec(**spec_overrides), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    for status in ("review", "scheduled", "running"):
        await svc.transition(
            exp.id, to_status=status, actor=admin,
            checklist=_CHECKLIST if status == "scheduled" else None,
        )
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    asvc = AssignmentService(db)
    for i in range(20):
        await asvc.resolve(experiment_key=exp.key, unit_type="user", unit_id=f"d-{i}")
        if i % 2 == 0:
            await asvc.record_exposure(experiment_key=exp.key, unit_type="user", unit_id=f"d-{i}")
    start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=start, window_end=start + timedelta(days=1)
    )
    for status in ("completed", "analyzed"):
        await svc.transition(
            exp.id, to_status=status, actor=admin,
            checklist=_CHECKLIST if status == "scheduled" else None,
        )
    analysis = await AnalysisService(db).run(exp.id, actor=admin)
    return exp, admin, analysis["result_hash"]


async def _promote(db, exp, admin, result_hash):
    return await DecisionService(db).create(
        exp.id, decision="promote", summary="treatment wins with adequate power",
        analysis_result_hash=result_hash, actor=admin,
    )


# ── Decisions ────────────────────────────────────────────────────────


async def test_promote_decision_transitions_and_records(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    record = await _promote(db, exp, admin, result_hash)
    assert record.decision == "promote"
    assert record.domain == "learning"
    assert record.analysis_type == "randomized"
    assert record.guardrail_outcome["clean"] is True
    assert (await ExperimentService(db).get(exp.id)).status == "promoted"


async def test_decision_requires_recorded_analysis_hash(db):
    exp, admin, _ = await _mk_analyzed(db)
    with pytest.raises(AppError) as e:
        await DecisionService(db).create(
            exp.id, decision="promote", summary="hash forged from thin air x",
            analysis_result_hash="f" * 64, actor=admin,
        )
    assert e.value.code == "DECISION_HASH_MISMATCH"


async def test_decision_requires_analyzed_status(db):
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    exp = await ExperimentService(db).create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    with pytest.raises(AppError) as e:
        await DecisionService(db).create(
            exp.id, decision="promote", summary="way too early to decide this",
            analysis_result_hash="a" * 64, actor=admin,
        )
    assert e.value.code == "DECISION_STATE_INVALID"


async def test_terminal_decision_unique(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    await _promote(db, exp, admin, result_hash)
    # promoted is terminal — a second decision fails on status already
    with pytest.raises(AppError):
        await DecisionService(db).create(
            exp.id, decision="reject", summary="contradictory second decision",
            analysis_result_hash=result_hash, actor=admin,
        )


async def test_extend_pushes_close_date_and_stays_analyzed(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    before = (await ExperimentService(db).get(exp.id)).analysis_close_at
    await DecisionService(db).create(
        exp.id, decision="extend", summary="long-term outcomes still maturing",
        analysis_result_hash=result_hash, actor=admin, extend_days=45,
    )
    exp_row = await ExperimentService(db).get(exp.id)
    assert exp_row.status == "analyzed"
    assert exp_row.analysis_close_at == before + timedelta(days=45)
    # extend may repeat
    await DecisionService(db).create(
        exp.id, decision="inconclusive", summary="still not enough signal here",
        analysis_result_hash=result_hash, actor=admin,
    )


async def test_direct_transition_to_promoted_refused(db):
    """The generic transition endpoint must never mint promoted/rejected —
    those are decision outcomes (approver + verified hash), otherwise the
    registry is optional and the hash gate decorative."""
    exp, admin, result_hash = await _mk_analyzed(db)
    svc = ExperimentService(db)
    for status in ("promoted", "rejected"):
        with pytest.raises(AppError) as e:
            await svc.transition(
            exp.id, to_status=status, actor=admin,
            checklist=_CHECKLIST if status == "scheduled" else None,
        )
        assert e.value.code == "EXPERIMENT_DECISION_REQUIRED"
    # the decision path still works
    await _promote(db, exp, admin, result_hash)
    assert (await svc.get(exp.id)).status == "promoted"


async def test_surface_key_reusable_after_terminal(db):
    """Keys are unique among LIVE experiments only — archiving releases the
    surface key for the next experiment; resolution binds to the live one."""
    from app.experiments.services.assignment import AssignmentService, forget_missing_key

    exp, admin, result_hash = await _mk_analyzed(db)
    key = exp.key
    await _promote(db, exp, admin, result_hash)  # terminal: promoted
    svc = ExperimentService(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    second = await svc.create(
        key=key, title="second run on the surface", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    assert second.id != exp.id
    await svc.create_version(second.id, spec=_spec(), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=second.id, slice_start=0, slice_end=9999
    )
    for status in ("review", "scheduled", "running"):
        await svc.transition(
            second.id, to_status=status, actor=admin,
            checklist=_CHECKLIST if status == "scheduled" else None,
        )
    await svc.set_ramp(second.id, ramp_bp=10_000, actor=admin)
    forget_missing_key(key)
    resolved = await AssignmentService(db).resolve(
        experiment_key=key, unit_type="user", unit_id="reuse-1"
    )
    assert resolved is not None  # binds to the LIVE experiment
    # ...but a second LIVE experiment on the key is still refused
    with pytest.raises(AppError) as e:
        await svc.create(
            key=key, title="third", domain="learning",
            layer_key=layer.key, owner_user_id=admin.id,
        )
    assert e.value.code == "EXPERIMENT_KEY_TAKEN"


async def test_observational_cannot_promote(db):
    exp, admin, result_hash = await _mk_analyzed(db, analysis_type="observational")
    with pytest.raises(AppError) as e:
        await _promote(db, exp, admin, result_hash)
    assert e.value.code == "PROMOTION_REQUIRES_RANDOMIZED"


# ── Registry search & meta ───────────────────────────────────────────


async def test_search_escapes_like_metacharacters(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    await DecisionService(db).create(
        exp.id, decision="inconclusive", summary="lift was 100% exactly as absurd",
        analysis_result_hash=result_hash, actor=admin,
    )
    svc = DecisionService(db)
    hit, _, _ = await svc.search(q="100%")
    assert any("100%" in r.summary for r in hit)
    # '%' must not act as a wildcard: 'l%d' would match 'lift ... absurd'
    miss, _, _ = await svc.search(q="l%d")
    assert all("l%d" in r.summary for r in miss)


async def test_meta_counts_and_win_rate(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    await _promote(db, exp, admin, result_hash)
    meta = await DecisionService(db).meta(domain="learning")
    assert meta["by_decision"].get("promote", 0) >= 1
    assert meta["win_rate"] is None or 0.0 <= meta["win_rate"] <= 1.0


# ── Promotion drafts ─────────────────────────────────────────────────


async def _mk_matching_config(db) -> MatchingConfig:
    config = MatchingConfig(
        # target_entity_type is String(30) — keep the random suffix short
        version=1, target_entity_type=f"exp-{str(ULID()).lower()[-10:]}",
        weights={"skill_fit": 0.6, "history": 0.4},
        thresholds={"reason_min": 0.7},
    )
    db.add(config)
    await db.flush()
    return config


async def test_promotion_full_lifecycle_matching_config(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    base = await _mk_matching_config(db)
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        decision.id, target_type="matching_config", target_ref=base.id,
        draft_payload={"weights": {"skill_fit": 0.7, "history": 0.3}}, actor=admin,
    )
    assert draft.status == "draft"
    # apply before approve refused
    with pytest.raises(AppError) as e:
        await psvc.apply(draft.id, actor=admin)
    assert e.value.code == "DECISION_STATE_INVALID"
    await psvc.approve(draft.id, actor=admin)
    applied = await psvc.apply(draft.id, actor=admin)
    assert applied.status == "applied"
    assert applied.applied_ref is not None
    new_config = await db.get(MatchingConfig, applied.applied_ref)
    assert new_config.is_active is False  # DRAFT — activation is matching's call
    assert new_config.version == base.version + 1
    assert new_config.weights == {"skill_fit": 0.7, "history": 0.3}
    assert (await db.get(MatchingConfig, base.id)).weights == {
        "skill_fit": 0.6, "history": 0.4,
    }  # base row never mutated
    # idempotency
    with pytest.raises(AppError) as e:
        await psvc.apply(draft.id, actor=admin)
    assert e.value.code == "PROMOTION_ALREADY_APPLIED"


async def test_promotion_draft_requires_promote_decision(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    record = await DecisionService(db).create(
        exp.id, decision="inconclusive", summary="not enough evidence to ship",
        analysis_result_hash=result_hash, actor=admin,
    )
    with pytest.raises(AppError) as e:
        await PromotionService(db).create_draft(
            record.id, target_type="matching_config", target_ref="a" * 26,
            draft_payload={}, actor=admin,
        )
    assert e.value.code == "DECISION_STATE_INVALID"


async def test_promotion_rejects_unknown_and_employment_targets(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    for target in ("offer", "hire", "auto_reject", "talent_ranking"):
        with pytest.raises(AppError) as e:
            await PromotionService(db).create_draft(
                decision.id, target_type=target, target_ref="a" * 26,
                draft_payload={}, actor=admin,
            )
        assert e.value.code == "VALIDATION_ERROR", target


async def test_matching_weights_must_sum_to_one(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    base = await _mk_matching_config(db)
    with pytest.raises(AppError) as e:
        await PromotionService(db).create_draft(
            decision.id, target_type="matching_config", target_ref=base.id,
            draft_payload={"weights": {"skill_fit": 0.9, "history": 0.3}}, actor=admin,
        )
    assert "sum to 1.0" in e.value.message


async def test_unwired_target_refuses_apply_explicitly(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        decision.id, target_type="pack_recommendation", target_ref="a" * 26,
        draft_payload={}, actor=admin,
    )
    await psvc.approve(draft.id, actor=admin)
    with pytest.raises(AppError) as e:
        await psvc.apply(draft.id, actor=admin)
    assert e.value.code == "EXPERIMENT_PROMOTION_UNWIRED"
    assert (await psvc.get(draft.id)).status == "approved"  # never silently applied


async def test_learning_path_apply_creates_draft_path(db):
    from app.models.learning_path import LearningPath
    from app.models.organization import Organization
    from app.models.skill import ContentStatus

    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    # minimal org + base path
    from app.controlplane.models.tenant import TenantAccount

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}", slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(
        name=f"o-{str(ULID()).lower()}", slug=f"o-{str(ULID()).lower()}", tenant_id=tenant.id
    )
    db.add(org)
    await db.flush()
    base = LearningPath(
        org_id=org.id, name="Base path", slug=f"base-{str(ULID()).lower()}",
        status=ContentStatus.PUBLISHED,
    )
    db.add(base)
    await db.flush()
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        decision.id, target_type="learning_path", target_ref=base.id,
        draft_payload={"name": "Improved ordering"}, actor=admin,
    )
    await psvc.approve(draft.id, actor=admin)
    applied = await psvc.apply(draft.id, actor=admin)
    new_path = await db.get(LearningPath, applied.applied_ref)
    assert new_path.status == ContentStatus.DRAFT  # never rewrites the live path
    assert new_path.name == "Improved ordering"
    assert (await db.get(LearningPath, base.id)).status == ContentStatus.PUBLISHED


async def test_workflow_binding_apply_creates_unconfirmed_suggestion(db):
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization
    from app.models.provider import ProviderAdapter, ProviderConnection, ProviderModelOffering
    from app.models.workflow_pack import WorkflowPackInstallation
    from app.models.workflow_run import WorkflowStepBinding

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}", slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(
        name=f"o-{str(ULID()).lower()}", slug=f"o-{str(ULID()).lower()}", tenant_id=tenant.id
    )
    db.add(org)
    await db.flush()
    adapter = ProviderAdapter(key=f"mock-{str(ULID()).lower()[-8:]}", name="Mock")
    db.add(adapter)
    await db.flush()
    conn = ProviderConnection(org_id=org.id, adapter_id=adapter.id, name="c", status="active")
    db.add(conn)
    await db.flush()
    offering = ProviderModelOffering(
        connection_id=conn.id, capability_key="text.generate", model_name="m", is_active=True
    )
    installation = WorkflowPackInstallation(org_id=org.id, installed_version="1.0.0")
    db.add_all([offering, installation])
    await db.flush()

    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        decision.id, target_type="workflow_binding", target_ref=installation.id,
        draft_payload={"step_id": "step-1", "offering_id": offering.id}, actor=admin,
    )
    await psvc.approve(draft.id, actor=admin)
    applied = await psvc.apply(draft.id, actor=admin)
    binding = await db.get(WorkflowStepBinding, applied.applied_ref)
    assert binding.confirmed_by is None  # UNCONFIRMED — a human must confirm (D5)
    assert binding.offering_id == offering.id
    assert binding.installation_id == installation.id


async def test_workflow_binding_apply_never_overwrites_existing(db):
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization
    from app.models.provider import ProviderAdapter, ProviderConnection, ProviderModelOffering
    from app.models.workflow_pack import WorkflowPackInstallation
    from app.models.workflow_run import WorkflowStepBinding

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}", slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(
        name=f"o-{str(ULID()).lower()}", slug=f"o-{str(ULID()).lower()}", tenant_id=tenant.id
    )
    db.add(org)
    await db.flush()
    adapter = ProviderAdapter(key=f"mock-{str(ULID()).lower()[-8:]}", name="Mock")
    db.add(adapter)
    await db.flush()
    conn = ProviderConnection(org_id=org.id, adapter_id=adapter.id, name="c", status="active")
    db.add(conn)
    await db.flush()
    offering = ProviderModelOffering(
        connection_id=conn.id, capability_key="text.generate", model_name="m", is_active=True
    )
    installation = WorkflowPackInstallation(org_id=org.id, installed_version="1.0.0")
    db.add_all([offering, installation])
    await db.flush()
    db.add(
        WorkflowStepBinding(
            org_id=org.id, installation_id=installation.id, step_id="step-1",
            binding_mode="confirmed", offering_id=offering.id,
        )
    )
    await db.flush()

    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        decision.id, target_type="workflow_binding", target_ref=installation.id,
        draft_payload={"step_id": "step-1", "offering_id": offering.id}, actor=admin,
    )
    await psvc.approve(draft.id, actor=admin)
    with pytest.raises(AppError) as e:
        await psvc.apply(draft.id, actor=admin)
    assert e.value.status_code == 409
    assert (await psvc.get(draft.id)).status == "approved"  # never silently applied


async def test_eco_rollout_apply_creates_draft_plan(db):
    from app.ecosystem.models.catalog import AIModel
    from app.ecosystem.models.replacement import ReplacementCandidate, RolloutPlan

    entity = AIModel(canonical_name="Cand", slug=f"cand-{str(ULID()).lower()}")
    db.add(entity)
    await db.flush()
    candidate = ReplacementCandidate(
        deprecated_kind="model", deprecated_id="d" * 26,
        candidate_kind="model", candidate_id=entity.id,
        hard_compatible=True,
    )
    db.add(candidate)
    await db.flush()

    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        decision.id, target_type="eco_rollout_policy", target_ref=candidate.id,
        draft_payload={"scope_type": "benchmark_only"}, actor=admin,
    )
    await psvc.approve(draft.id, actor=admin)
    applied = await psvc.apply(draft.id, actor=admin)
    plan = await db.get(RolloutPlan, applied.applied_ref)
    assert plan is not None
    assert plan.status == "draft"  # eco promote/reject stays an eco decision


async def test_eco_rollout_apply_refuses_hard_incompatible(db):
    """The eco domain's own gate re-runs at apply — promotion never bypasses
    the hard-incompatible red line."""
    from app.ecosystem.models.catalog import AIModel
    from app.ecosystem.models.replacement import ReplacementCandidate

    entity = AIModel(canonical_name="Bad", slug=f"bad-{str(ULID()).lower()}")
    db.add(entity)
    await db.flush()
    candidate = ReplacementCandidate(
        deprecated_kind="model", deprecated_id="d" * 26,
        candidate_kind="model", candidate_id=entity.id,
        hard_compatible=False,
    )
    db.add(candidate)
    await db.flush()

    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        decision.id, target_type="eco_rollout_policy", target_ref=candidate.id,
        draft_payload={"scope_type": "benchmark_only"}, actor=admin,
    )
    await psvc.approve(draft.id, actor=admin)
    with pytest.raises(AppError) as e:
        await psvc.apply(draft.id, actor=admin)
    assert e.value.code == "ECO_HARD_INCOMPATIBLE"
    assert (await psvc.get(draft.id)).status == "approved"


async def test_validate_target_error_contract(db):
    """Every _validate_target failure mode with BOTH code and HTTP status
    pinned (a mutated status constant must not survive), including the
    generic-branch checks that had no coverage."""
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization
    from app.models.provider import ProviderAdapter, ProviderConnection, ProviderModelOffering
    from app.models.workflow_pack import WorkflowPackInstallation

    svc = PromotionService(db)

    async def expect(code: str, status: int, target_type: str, target_ref: str, payload: dict):
        with pytest.raises(AppError) as e:
            await svc._validate_target(target_type, target_ref, payload)
        assert (e.value.code, e.value.status_code) == (code, status), (
            target_type, e.value.code, e.value.status_code,
        )

    # unknown target type
    await expect("VALIDATION_ERROR", 422, "bogus_target", "a" * 26, {})
    # matching_config: missing row / bad weights shape / bad weight sum
    await expect("EXPERIMENT_NOT_FOUND", 404, "matching_config", "m" * 26, {})
    base = await _mk_matching_config(db)
    await expect("VALIDATION_ERROR", 422, "matching_config", base.id, {"weights": {}})
    await expect("VALIDATION_ERROR", 422, "matching_config", base.id, {"weights": "nope"})
    await expect(
        "VALIDATION_ERROR", 422, "matching_config", base.id,
        {"weights": {"a": 0.5, "b": 0.6}},
    )
    # learning_path: missing row
    await expect("EXPERIMENT_NOT_FOUND", 404, "learning_path", "l" * 26, {})
    # workflow_binding: missing installation / missing fields / missing
    # offering / cross-org offering
    await expect("EXPERIMENT_NOT_FOUND", 404, "workflow_binding", "w" * 26, {})
    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}", slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org_a = Organization(
        name=f"a-{str(ULID()).lower()}", slug=f"a-{str(ULID()).lower()}", tenant_id=tenant.id
    )
    org_b = Organization(
        name=f"b-{str(ULID()).lower()}", slug=f"b-{str(ULID()).lower()}", tenant_id=tenant.id
    )
    db.add_all([org_a, org_b])
    await db.flush()
    installation = WorkflowPackInstallation(org_id=org_a.id, installed_version="1.0.0")
    adapter = ProviderAdapter(key=f"mock-{str(ULID()).lower()[-8:]}", name="Mock")
    db.add_all([installation, adapter])
    await db.flush()
    conn_b = ProviderConnection(org_id=org_b.id, adapter_id=adapter.id, name="c", status="active")
    db.add(conn_b)
    await db.flush()
    offering_b = ProviderModelOffering(
        connection_id=conn_b.id, capability_key="text.generate", model_name="m", is_active=True
    )
    db.add(offering_b)
    await db.flush()
    await expect(
        "VALIDATION_ERROR", 422, "workflow_binding", installation.id, {"step_id": "s"}
    )
    await expect(
        "EXPERIMENT_NOT_FOUND", 404, "workflow_binding", installation.id,
        {"step_id": "s", "offering_id": "o" * 26},
    )
    await expect(  # offering belongs to org_b, installation to org_a (R3)
        "VALIDATION_ERROR", 422, "workflow_binding", installation.id,
        {"step_id": "s", "offering_id": offering_b.id},
    )
    # eco_rollout_policy: missing candidate
    await expect("EXPERIMENT_NOT_FOUND", 404, "eco_rollout_policy", "e" * 26, {})
    # generic branch (pack_recommendation): oversize + blank refs
    await expect("VALIDATION_ERROR", 422, "pack_recommendation", "x" * 65, {})
    await expect("VALIDATION_ERROR", 422, "pack_recommendation", "   ", {})
    # generic branch happy path: plain refs pass, INCLUDING the 64-char
    # boundary (len > 64 rejects; len == 64 is legal)
    await svc._validate_target("pack_recommendation", "a" * 26, {})
    await svc._validate_target("pack_recommendation", "x" * 64, {})


async def test_unwired_targets_are_only_presentation_pair(db):
    """pack_recommendation / pricing_presentation stay explicitly unwired
    (no target-domain draft store) — pin the set so a new unwired target
    can't appear silently."""
    from app.experiments.security import PROMOTION_TARGET_TYPES

    wired = {"matching_config", "learning_path", "workflow_binding", "eco_rollout_policy"}
    assert PROMOTION_TARGET_TYPES - wired == {"pack_recommendation", "pricing_presentation"}


async def test_decide_after_repeated_identical_looks(db):
    """Wave-32: the SAME result hash recorded by multiple looks is perfectly
    legal (unchanged data, repeated runs) — the hash-exists probe must stay
    a limit-1 EXISTS, not a scalar that explodes on the second row. Also
    pins the guardrail_outcome's experiment scoping: a NEIGHBOR experiment's
    events must not leak into the decision record."""

    from app.experiments.models import GuardrailEvent

    exp, admin, result_hash = await _mk_analyzed(db)
    # a second identical look (same snapshots -> same hash)
    from app.experiments.services.analysis_service import AnalysisService

    second = await AnalysisService(db).run(exp.id, actor=admin)
    assert second["result_hash"] == result_hash  # deterministic hash

    # neighbor experiment's guardrail event must NOT leak into the outcome
    neighbor, _n_admin, _n_hash = await _mk_analyzed(db)
    db.add(GuardrailEvent(experiment_id=neighbor.id, guardrail_key="cost_usd",
                          action="paused", auto=True, detail={}))
    db.add(GuardrailEvent(experiment_id=exp.id, guardrail_key="cost_usd",
                          action="alerted", auto=True, detail={}))
    await db.flush()

    record = await DecisionService(db).create(
        exp.id, decision="promote", summary="repeated looks are legal",
        analysis_result_hash=result_hash, actor=admin,
    )
    outcome = record.guardrail_outcome
    assert outcome["clean"] is False
    assert outcome["events"] == [
        {"guardrail_key": "cost_usd", "action": "alerted", "count": 1}
    ]  # exactly OUR event; the neighbor's paused event stays out
    # round 239: the cited look's warnings FREEZE into the record — the
    # audit outlives event retention and history limits
    assert record.evidence["cited_warnings"] == second["warnings"]


async def test_concurrent_decides_single_terminal_record(db):
    """Round 155: two racing PROMOTE decisions must leave exactly ONE
    terminal record and one DECISION_STATE_INVALID loser — the terminal
    unique constraint is the backstop and the service maps its violation to
    a typed 409 (never a raw 500), with the experiment promoted exactly
    once."""
    import asyncio

    from sqlalchemy import func as _func
    from sqlalchemy import select as _select

    exp, admin, result_hash = await _mk_analyzed(db)
    exp_id, admin_id = exp.id, admin.id
    await db.commit()  # racing sessions need committed state

    async def decide_once():
        async with AsyncSessionLocal() as session:
            actor = await session.get(User, admin_id)
            try:
                await DecisionService(session).create(
                    exp_id, decision="promote", summary="race",
                    analysis_result_hash=result_hash, actor=actor,
                )
                await session.commit()
                return "decided"
            except AppError as e:
                return e.code

    try:
        results = await asyncio.gather(decide_once(), decide_once())
        assert sorted(results) == ["DECISION_STATE_INVALID", "decided"], results
        async with AsyncSessionLocal() as session:
            from app.experiments.models import DecisionRecord as DecisionRec
            from app.experiments.models import Experiment as ExpModel

            count = (
                await session.execute(
                    _select(_func.count()).select_from(DecisionRec).where(
                        DecisionRec.experiment_id == exp_id,
                        DecisionRec.decision.in_(("promote", "reject")),
                    )
                )
            ).scalar_one()
            assert count == 1
            assert (await session.get(ExpModel, exp_id)).status == "promoted"
    finally:
        # committed-session law: racing tests COMMIT, so they must sweep
        # their own debris (the promoted decision pollutes the corpus
        # prior, the experiment pollutes the digest/time sweeps)
        async with AsyncSessionLocal() as session:
            from sqlalchemy import delete as _delete

            from app.experiments.models import Experiment as ExpModel
            from app.experiments.models import ExperimentLayer as LayerModel

            exp_row = await session.get(ExpModel, exp_id)
            layer_key = exp_row.layer_key if exp_row else None
            await session.execute(_delete(ExpModel).where(ExpModel.id == exp_id))
            if layer_key:
                await session.execute(
                    _delete(LayerModel).where(LayerModel.key == layer_key)
                )
            await session.execute(_delete(User).where(User.id == admin_id))
            await session.commit()


async def test_concurrent_apply_single_target_draft(db):
    """Two racing applies must produce exactly ONE target-domain draft and
    one PROMOTION_ALREADY_APPLIED loser (the draft row is FOR-UPDATE locked;
    without it both pass the idempotency check and double-create)."""
    import asyncio

    from sqlalchemy import func as _func
    from sqlalchemy import select as _select

    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    base = await _mk_matching_config(db)
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        decision.id, target_type="matching_config", target_ref=base.id,
        draft_payload={"weights": {"skill_fit": 0.7, "history": 0.3}}, actor=admin,
    )
    await psvc.approve(draft.id, actor=admin)
    draft_id, admin_id, entity_type = draft.id, admin.id, base.target_entity_type
    await db.commit()  # racing sessions need committed state

    async def apply_once():
        async with AsyncSessionLocal() as session:
            actor = await session.get(User, admin_id)
            try:
                await PromotionService(session).apply(draft_id, actor=actor)
                await session.commit()
                return "applied"
            except AppError as e:
                return e.code

    try:
        results = await asyncio.gather(apply_once(), apply_once())
        assert sorted(results) == ["PROMOTION_ALREADY_APPLIED", "applied"], results
        async with AsyncSessionLocal() as session:
            versions = (
                await session.execute(
                    _select(_func.count()).where(
                        MatchingConfig.target_entity_type == entity_type
                    )
                )
            ).scalar_one()
            assert versions == 2  # base + exactly ONE new draft version
    finally:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import delete as _delete

            from app.experiments.models import Experiment, ExperimentLayer

            exp_row = await session.get(Experiment, exp.id)
            layer_key = exp_row.layer_key if exp_row else None
            await session.execute(_delete(Experiment).where(Experiment.id == exp.id))
            if layer_key:
                await session.execute(
                    _delete(ExperimentLayer).where(ExperimentLayer.key == layer_key)
                )
            await session.execute(
                _delete(MatchingConfig).where(
                    MatchingConfig.target_entity_type == entity_type
                )
            )
            await session.execute(_delete(User).where(User.id == admin_id))
            await session.commit()


async def test_scope_org_missing_is_404_not_key_taken(db):
    """A bogus scope_org_id must 404 — the FK violation was previously
    swallowed by the IntegrityError→EXPERIMENT_KEY_TAKEN mapping."""
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    with pytest.raises(AppError) as e:
        await ExperimentService(db).create(
            key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
            layer_key=layer.key, owner_user_id=admin.id, scope_org_id="x" * 26,
        )
    assert e.value.code == "EXPERIMENT_NOT_FOUND"
    assert e.value.status_code == 404


async def test_oversized_spec_rejected(db):
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    exp = await ExperimentService(db).create(
        key=f"exp-{str(ULID()).lower()}", title="T", domain="learning",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    spec = _spec()
    spec["population"] = {
        "rules": [{"field": "cohort_id", "op": "in", "values": ["c" * 400] * 180}]
    }
    with pytest.raises(AppError) as e:
        await ExperimentService(db).create_version(exp.id, spec=spec, actor=admin)
    assert e.value.code == "EXPERIMENT_SPEC_INVALID"
    assert "too large" in e.value.message


async def test_draft_registry_status_filter(db):
    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    base = await _mk_matching_config(db)
    psvc = PromotionService(db)
    await psvc.create_draft(
        decision.id, target_type="matching_config", target_ref=base.id,
        draft_payload={}, actor=admin,
    )
    drafts = await psvc.list_drafts(status="draft")
    assert any(d.decision_record_id == decision.id for d in drafts)
    assert all(d.status == "draft" for d in drafts)


# ── Async apply through the outbox (v2 batch 6, apply_error lands) ───


async def _approved_draft(db, target_type="pack_recommendation", **kwargs):
    exp, admin, result_hash = await _mk_analyzed(db)
    decision = await _promote(db, exp, admin, result_hash)
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        decision.id, target_type=target_type,
        target_ref=kwargs.pop("target_ref", "a" * 26),
        draft_payload=kwargs.pop("draft_payload", {}), actor=admin,
    )
    await psvc.approve(draft.id, actor=admin)
    return draft, admin, psvc


async def test_async_apply_parks_then_handler_lands_failure_in_apply_error(db):
    """The unwired target fails TYPED in the handler: the draft returns to
    'approved' with apply_error recorded — retryable, never stuck, and the
    outbox message is consumed (no redelivery loop)."""
    from sqlalchemy import select as _select

    from app.controlplane.models.outbox import OutboxMessage
    from app.experiments.worker import handle_apply_promotion

    draft, admin, psvc = await _approved_draft(db)
    parked = await psvc.apply_async(draft.id, actor=admin)
    assert parked.status == "applying"
    assert parked.apply_error is None
    message = (
        await db.execute(
            _select(OutboxMessage).where(
                OutboxMessage.topic == "exp.apply_promotion",
                OutboxMessage.status == "pending",
            ).order_by(OutboxMessage.id.desc()).limit(1)
        )
    ).scalar_one()
    assert message.payload["draft_id"] == draft.id

    # while in flight, both sync and a second async apply refuse
    with pytest.raises(AppError) as e:
        await psvc.apply(draft.id, actor=admin)
    assert e.value.code == "PROMOTION_APPLY_IN_FLIGHT"
    with pytest.raises(AppError) as e:
        await psvc.apply_async(draft.id, actor=admin)
    assert e.value.code == "PROMOTION_APPLY_IN_FLIGHT"

    await handle_apply_promotion(db, message.payload)
    row = await psvc.get(draft.id)
    assert row.status == "approved"  # returned, not stuck in applying
    assert "EXPERIMENT_PROMOTION_UNWIRED" in row.apply_error
    # retryable: queue it again
    again = await psvc.apply_async(draft.id, actor=admin)
    assert again.status == "applying"
    assert again.apply_error is None


async def test_async_apply_success_lands_applied_ref(db):
    from app.controlplane.models.tenant import TenantAccount
    from app.experiments.worker import handle_apply_promotion
    from app.models.learning_path import LearningPath
    from app.models.organization import Organization
    from app.models.skill import ContentStatus

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}", slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(
        name=f"o-{str(ULID()).lower()}", slug=f"o-{str(ULID()).lower()}", tenant_id=tenant.id
    )
    db.add(org)
    await db.flush()
    base = LearningPath(
        org_id=org.id, name="Base path", slug=f"base-{str(ULID()).lower()}",
        status=ContentStatus.PUBLISHED,
    )
    db.add(base)
    await db.flush()
    draft, admin, psvc = await _approved_draft(
        db, target_type="learning_path", target_ref=base.id,
        draft_payload={"name": "Async ordering"},
    )
    await psvc.apply_async(draft.id, actor=admin)
    await handle_apply_promotion(db, {"draft_id": draft.id, "actor_user_id": admin.id})
    row = await psvc.get(draft.id)
    assert row.status == "applied"
    assert row.apply_error is None
    new_path = await db.get(LearningPath, row.applied_ref)
    assert new_path.status == ContentStatus.DRAFT


async def test_typed_apply_failure_discards_partial_adapter_writes(db, monkeypatch):
    """Defect #47 (the #41 family): the typed-failure branch keeps the
    transaction and parks the draft back to 'approved' — so partial writes
    an adapter made BEFORE raising must roll back to the savepoint, never
    ride along with the parking. Pinned with an adapter that writes a row
    and then fails typed."""
    from ulid import ULID as _ULID

    from app.exceptions import AppError as _AppError
    from app.experiments.services.promotion import PromotionService
    from app.experiments.worker import handle_apply_promotion
    from app.models.user import User as _User
    from app.models.user import UserRole as _Role
    from app.models.user import UserStatus as _Status

    marker_email = f"partial-{_ULID()}@example.com"

    async def _write_then_fail(self, draft, actor):
        self.db.add(_User(email=marker_email, display_name="P",
                          role=_Role.STUDENT, status=_Status.ACTIVE))
        await self.db.flush()
        raise _AppError("EXPERIMENT_PROMOTION_UNWIRED", "typed failure after write", 422)

    monkeypatch.setattr(PromotionService, "_apply_adapter", _write_then_fail)

    draft, admin, psvc = await _approved_draft(db)
    await psvc.apply_async(draft.id, actor=admin)
    await handle_apply_promotion(db, {"draft_id": draft.id, "actor_user_id": admin.id})
    row = await psvc.get(draft.id)
    assert row.status == "approved"
    assert row.apply_error and "typed failure after write" in row.apply_error
    # the partial adapter write is GONE
    from sqlalchemy import select as _select

    leaked = (
        await db.execute(_select(_User.id).where(_User.email == marker_email))
    ).scalar_one_or_none()
    assert leaked is None


async def test_async_handler_skips_when_race_already_resolved(db):
    """A racing manual path that already moved the draft out of 'applying'
    wins; the handler is a no-op (idempotent at-least-once delivery)."""
    from app.experiments.worker import handle_apply_promotion

    draft, admin, psvc = await _approved_draft(db)
    # never parked — handler must not touch an 'approved' draft
    await handle_apply_promotion(db, {"draft_id": draft.id, "actor_user_id": admin.id})
    row = await psvc.get(draft.id)
    assert row.status == "approved"
    assert row.apply_error is None


def test_error_status_contract_pinned_by_source():
    """Round-20 mutation lesson (the round-6 one recurring): every AppError's
    HTTP status in the decision/promotion services is part of the API
    contract — pin the full (code → status) map straight from the AST so a
    single flipped constant anywhere fails here."""
    import ast
    from pathlib import Path

    services = Path(__file__).resolve().parents[1] / "app" / "experiments" / "services"
    found: dict[str, set[int]] = {}
    for name in ("decisions.py", "promotion.py"):
        tree = ast.parse((services / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "AppError"
                and len(node.args) >= 3
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[2], ast.Constant)
            ):
                found.setdefault(node.args[0].value, set()).add(node.args[2].value)

    assert found == {
        "DECISION_HASH_MISMATCH": {422},
        "DECISION_STATE_INVALID": {409, 422},
        "EXPERIMENT_NOT_FOUND": {404},
        "EXPERIMENT_PROMOTION_UNWIRED": {422},
        "EXPERIMENT_SPEC_INVALID": {422},
        "PROMOTION_ALREADY_APPLIED": {409},
        "PROMOTION_APPLY_IN_FLIGHT": {409},
        "PROMOTION_REQUIRES_RANDOMIZED": {422},
        "VALIDATION_ERROR": {422},
    }, found


async def test_decision_optional_fields_default_to_empty_dicts(db):
    """`x or {}` killers: omitted uncertainty/segments/evidence land as {}
    (an Or→And flip would hand None to non-null JSONB columns)."""
    exp, admin, result_hash = await _mk_analyzed(db)
    record = await DecisionService(db).create(
        exp.id, decision="inconclusive", summary="defaults pinned",
        analysis_result_hash=result_hash, actor=admin,
    )
    assert record.uncertainty == {}
    assert record.segments == {}
    assert record.evidence == {}


async def test_inconclusive_never_extends_the_close(db):
    """`decision == "extend" and close_at` killer: an inconclusive decision
    on an experiment WITH a close date must not move it (And→Or would)."""
    from datetime import UTC, datetime, timedelta

    exp, admin, result_hash = await _mk_analyzed(db)
    close_at = datetime(2026, 12, 1, tzinfo=UTC)
    exp.analysis_close_at = close_at
    await db.flush()
    await DecisionService(db).create(
        exp.id, decision="inconclusive", summary="no extension",
        analysis_result_hash=result_hash, actor=admin,
    )
    await db.refresh(exp)
    assert exp.analysis_close_at == close_at
    # and extend DOES move it, by exactly the requested days
    await DecisionService(db).create(
        exp.id, decision="extend", summary="two more weeks",
        analysis_result_hash=result_hash, actor=admin, extend_days=14,
    )
    await db.refresh(exp)
    assert exp.analysis_close_at == close_at + timedelta(days=14)


async def test_meta_distinguishes_randomized_terminal_and_promoted(db):
    """Meta-aggregation killers: the corpus counters must split by
    analysis_type AND by decision (promote vs reject)."""
    svc = DecisionService(db)
    exp1, admin, h1 = await _mk_analyzed(db)
    await svc.create(exp1.id, decision="promote", summary="win",
                     analysis_result_hash=h1, actor=admin)
    exp2, admin2, h2 = await _mk_analyzed(db)
    await svc.create(exp2.id, decision="reject", summary="loss",
                     analysis_result_hash=h2, actor=admin2)
    # asymmetric promote count (2:1) — a promote==/!= flip must move win_rate
    exp2b, admin2b, h2b = await _mk_analyzed(db)
    await svc.create(exp2b.id, decision="promote", summary="second win",
                     analysis_result_hash=h2b, actor=admin2b)
    # an OBSERVATIONAL reject must not enter the randomized win-rate pool
    exp3, admin3, h3 = await _mk_analyzed(db, analysis_type="observational")
    await svc.create(exp3.id, decision="reject", summary="assoc only",
                     analysis_result_hash=h3, actor=admin3)
    meta = await svc.meta(domain="learning")
    assert meta["by_decision"]["promote"] == 2
    assert meta["by_decision"]["reject"] == 2
    # randomized pool: exactly 2 promote / 3 terminal — the observational
    # reject is excluded (And→Or) and promote vs reject counting (Eq→NotEq)
    # both pinned by the ASYMMETRIC 2:1 split
    assert abs(meta["win_rate"] - 2 / 3) < 1e-12


async def test_decision_cold_arms_necropsy(db):
    """Round 81 (dynamic triggers for arms the AST contract pins only
    statically): unknown decision 422, poison stored spec 422, duplicate
    decision -> typed IntegrityError mapping, get 404, list filters and
    keyset cursor."""
    from sqlalchemy import update as _update

    from app.experiments.models import ExperimentVersion as VersionModel

    exp, admin, result_hash = await _mk_analyzed(db)
    svc = DecisionService(db)

    with pytest.raises(AppError) as exc:
        await svc.create(exp.id, decision="banana", summary="x" * 12,
                         analysis_result_hash=result_hash, actor=admin)
    assert exc.value.code == "VALIDATION_ERROR" and exc.value.status_code == 422

    # a second analyzed experiment with a CORRUPTED stored spec
    exp2, admin2, hash2 = await _mk_analyzed(db)
    await db.execute(
        _update(VersionModel)
        .where(VersionModel.experiment_id == exp2.id, VersionModel.version == 1)
        .values(spec={"hypothesis": "bad"})
    )
    with pytest.raises(AppError) as exc:
        await svc.create(exp2.id, decision="promote", summary="y" * 12,
                         analysis_result_hash=hash2, actor=admin2)
    assert exc.value.code == "EXPERIMENT_SPEC_INVALID"

    # duplicate decision on the same experiment -> typed, never raw 500
    first = await svc.create(exp.id, decision="reject", summary="z" * 12,
                             analysis_result_hash=result_hash, actor=admin)
    assert first.decision == "reject"
    with pytest.raises(AppError) as exc:
        await svc.create(exp.id, decision="reject", summary="w" * 12,
                         analysis_result_hash=result_hash, actor=admin)
    assert exc.value.code in ("DECISION_STATE_INVALID",
                              "EXPERIMENT_INVALID_TRANSITION")

    with pytest.raises(AppError) as exc:
        await svc.get("0" * 26)
    assert exc.value.status_code == 404

    # list filters + keyset cursor
    rows, _total, _cur = await svc.search(domain=exp.domain, decision="reject")
    assert any(r.id == first.id for r in rows)
    rows2, _, _ = await svc.search(decision="promote")
    assert all(r.decision == "promote" for r in rows2)
    page1, _, _ = await svc.search(limit=1)
    if page1:
        page2, _, _ = await svc.search(limit=1, cursor=page1[0].id)
        assert all(r.id < page1[0].id for r in page2)


async def test_promotion_cold_arms_necropsy(db):
    """Round 82: promotion's state-guard arms triggered dynamically —
    defense-in-depth randomized check, draft 404, approve/reject/apply from
    wrong statuses — all typed, none raw."""
    from app.experiments.services.promotion import PromotionService

    exp, admin, result_hash = await _mk_analyzed(db)
    record = await _promote(db, exp, admin, result_hash)
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        record.id, target_type="pack_recommendation", target_ref="a" * 26,
        draft_payload={}, actor=admin,
    )

    with pytest.raises(AppError) as exc:
        await psvc.get("0" * 26)
    assert exc.value.status_code == 404

    # reject from draft works; approve AFTER reject is a typed 422
    await psvc.reject(draft.id, actor=admin)
    with pytest.raises(AppError) as exc:
        await psvc.approve(draft.id, actor=admin)
    assert exc.value.code == "DECISION_STATE_INVALID"
    # reject again from rejected: also typed
    with pytest.raises(AppError) as exc:
        await psvc.reject(draft.id, actor=admin)
    assert exc.value.code == "DECISION_STATE_INVALID"
    # apply from rejected: typed (not approved)
    with pytest.raises(AppError) as exc:
        await psvc.apply(draft.id, actor=admin)
    assert exc.value.code == "DECISION_STATE_INVALID"
