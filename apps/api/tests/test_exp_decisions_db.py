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
from app.experiments.services.analysis_service import AnalysisService
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.decisions import DecisionService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.layers import LayerService
from app.experiments.services.metrics import MetricService
from app.experiments.services.promotion import PromotionService
from app.models.matching import MatchingConfig
from app.models.user import User, UserRole, UserStatus


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
        await svc.transition(exp.id, to_status=status, actor=admin)
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
        await svc.transition(exp.id, to_status=status, actor=admin)
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
            await svc.transition(exp.id, to_status=status, actor=admin)
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
        await svc.transition(second.id, to_status=status, actor=admin)
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
