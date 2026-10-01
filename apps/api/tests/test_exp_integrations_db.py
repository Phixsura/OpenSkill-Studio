"""Domain integration hook tests (ADR-017 exp07, §7).

For every surface: the override applies only for treatment units, an INVALID
override falls back to control (the target domain's own validation is never
bypassed — R82 class), and an exposure is recorded exactly when the override
takes effect. The registry seam is exercised end-to-end through
RegistryService.search_packs.

Runs against the dev Postgres; rollback-per-test.
"""

import pytest
from sqlalchemy import func, select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.experiments import hooks
from app.experiments.models import ExperimentExposure
from app.experiments.security import ETHICS_CHECKLIST_KEY, LAUNCH_CHECKLIST_KEYS
from app.experiments.services.assignment import AssignmentService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.layers import LayerService
from app.experiments.services.metrics import MetricService
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


async def _mk_admin(db) -> User:
    user = User(
        email=f"exp-int-{ULID()}@example.com",
        display_name="I",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_surface_experiment(
    db, *, key: str, domain: str, unit_type: str, treatment_config: dict,
    control_weight_bp: int = 1,
):
    """Running experiment on a well-known surface key: control weight 1bp by
    default, treatment 9999bp — a resolved unit is a treatment unit with
    p=.9999 (pass control_weight_bp=9999 to flip).

    Surface keys are UNIQUE and other suites (the outbox-driving E2E) can
    leak a committed row into the dev DB — delete any residue first, inside
    this test's transaction (§106.25 accumulation law: never trust a shared
    dev DB to be empty)."""
    from sqlalchemy import delete

    from app.experiments.models import Experiment

    await db.execute(delete(Experiment).where(Experiment.key == key))
    await MetricService(db).ensure_seed_definitions()
    admin = await _mk_admin(db)
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain=domain)
    svc = ExperimentService(db)
    exp = await svc.create(
        key=key, title=f"surface {key}", domain=domain,
        layer_key=layer.key, owner_user_id=admin.id, risk_class="low",
    )
    spec = {
        "hypothesis": f"surface hook {key} applies overrides safely enough",
        "unit_type": unit_type,
        "variants": [
            {"key": "control", "name": "C", "weight_bp": control_weight_bp,
             "is_control": True},
            {"key": "treatment", "name": "T", "weight_bp": 10_000 - control_weight_bp,
             "config": treatment_config},
        ],
        "metrics": {
            "primary": ["exposure_rate"],
            "guardrails": [{"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}],
        },
    }
    await svc.create_version(exp.id, spec=spec, actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    for status in ("review", "scheduled", "running"):
        await svc.transition(
            exp.id, to_status=status, actor=admin,
            checklist=_CHECKLIST if status == "scheduled" else None,
        )
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    return exp, admin


async def _treatment_unit(db, exp, unit_type: str, prefix: str) -> str:
    """Find a unit id assigned to treatment (p=.9999 per try)."""
    asvc = AssignmentService(db)
    for i in range(20):
        unit_id = f"{prefix}-{i}"
        r = await asvc.resolve(experiment_key=exp.key, unit_type=unit_type, unit_id=unit_id)
        if r is not None and r.variant_key == "treatment":
            return unit_id
    raise AssertionError("no treatment unit in 20 tries (p < 1e-60)")


async def _exposures(db, experiment_id: str) -> int:
    return (
        await db.execute(
            select(func.count()).where(ExperimentExposure.experiment_id == experiment_id)
        )
    ).scalar_one()


# ── Matching (Part H) ────────────────────────────────────────────────


async def _mk_matching_pair(db):
    entity_type = f"exp-{str(ULID()).lower()[-10:]}"
    active = MatchingConfig(
        version=1, target_entity_type=entity_type,
        weights={"skill_fit": 1.0}, thresholds={}, is_active=True,
    )
    candidate = MatchingConfig(
        version=2, target_entity_type=entity_type,
        weights={"skill_fit": 0.5, "history": 0.5}, thresholds={}, is_active=False,
    )
    db.add_all([active, candidate])
    await db.flush()
    return entity_type, active, candidate


async def test_matching_override_serves_candidate_config(db):
    entity_type, _active, candidate = await _mk_matching_pair(db)
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_MATCHING_CONFIG, domain="matching",
        unit_type="organization",
        treatment_config={"matching_config_id": candidate.id},
    )
    org_unit = await _treatment_unit(db, exp, "organization", "org")
    result = await hooks.matching_config_override(
        db, org_id=org_unit, target_entity_type=entity_type
    )
    assert result is not None and result.id == candidate.id
    assert await _exposures(db, exp.id) == 1


async def test_matching_override_wrong_entity_type_falls_back(db):
    _entity_type, _active, candidate = await _mk_matching_pair(db)
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_MATCHING_CONFIG, domain="matching",
        unit_type="organization",
        treatment_config={"matching_config_id": candidate.id},
    )
    org_unit = await _treatment_unit(db, exp, "organization", "orgx")
    # Different entity type: the domain check refuses the override
    result = await hooks.matching_config_override(
        db, org_id=org_unit, target_entity_type="something-else"
    )
    assert result is None
    # defect #37: the fallback IS this unit's exposure (arm recorded)
    assert await _exposures(db, exp.id) == 1


# ── Workflow binding (Part G, R82 re-check) ──────────────────────────


async def _mk_offering(db, *, capability="text.generate", features=None, active=True):
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization
    from app.models.provider import ProviderAdapter, ProviderConnection, ProviderModelOffering

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
        connection_id=conn.id, capability_key=capability, model_name="m",
        features=features or ["json_mode"], is_active=active,
    )
    db.add(offering)
    await db.flush()
    return org, offering


async def test_binding_override_passes_capability_recheck(db):
    org, offering = await _mk_offering(db)
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_WORKFLOW_BINDING, domain="workflow",
        unit_type="workflow_installation",
        treatment_config={"offering_id": offering.id},
    )
    install_unit = await _treatment_unit(db, exp, "workflow_installation", "inst")
    result = await hooks.workflow_binding_override(
        db, installation_id=install_unit, org_id=org.id,
        capability="text.generate", required_features={"json_mode"},
    )
    assert result is not None and result.id == offering.id
    assert await _exposures(db, exp.id) == 1


async def test_binding_override_capability_mismatch_refused(db):
    org, offering = await _mk_offering(db, capability="text.generate")
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_WORKFLOW_BINDING, domain="workflow",
        unit_type="workflow_installation",
        treatment_config={"offering_id": offering.id},
    )
    install_unit = await _treatment_unit(db, exp, "workflow_installation", "instc")
    # The step's CURRENT capability differs (R82) — the experiment never
    # exempts the credential path
    assert await hooks.workflow_binding_override(
        db, installation_id=install_unit, org_id=org.id,
        capability="image.generate", required_features=set(),
    ) is None
    # Cross-org offering refused too
    assert await hooks.workflow_binding_override(
        db, installation_id=install_unit, org_id="x" * 26,
        capability="text.generate", required_features=set(),
    ) is None
    # Missing required feature refused
    assert await hooks.workflow_binding_override(
        db, installation_id=install_unit, org_id=org.id,
        capability="text.generate", required_features={"vision"},
    ) is None
    # defect #37: the fallback IS this unit's exposure (arm recorded)
    assert await _exposures(db, exp.id) == 1


async def test_binding_override_no_installation_skips(db):
    assert await hooks.workflow_binding_override(
        db, installation_id=None, org_id="o" * 26,
        capability="text.generate", required_features=set(),
    ) is None


# ── Registry ordering (marketplace presentation) ─────────────────────


async def test_registry_sort_override_end_to_end(db):
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_REGISTRY_ORDERING, domain="marketplace",
        unit_type="user", treatment_config={"sort": "most_installed"},
    )
    user_unit = await _treatment_unit(db, exp, "user", "viewer")
    assert await hooks.registry_sort_override(db, user_id=user_unit) == "most_installed"
    # End-to-end through the real seam: search_packs applies the override
    # for the viewer without raising (result ordering exercised by the
    # registry suite; here we pin the seam is live and fail-safe)
    from app.services.registry import RegistryService

    packs, _total = await RegistryService(db).search_packs(viewer_user_id=user_unit)
    assert isinstance(packs, list)
    assert await _exposures(db, exp.id) >= 1


async def test_registry_sort_override_rejects_unknown_sort(db):
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_REGISTRY_ORDERING, domain="marketplace",
        unit_type="user", treatment_config={"sort": "totally-bogus"},
    )
    user_unit = await _treatment_unit(db, exp, "user", "viewerx")
    assert await hooks.registry_sort_override(db, user_id=user_unit) is None
    # defect #37: the fallback IS this unit's exposure (arm recorded)
    assert await _exposures(db, exp.id) == 1


# ── Cohort path structure (Part F) ───────────────────────────────────


async def test_cohort_path_override_same_org_only(db):
    from app.controlplane.models.tenant import TenantAccount
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
    alt = LearningPath(
        org_id=org.id, name="Alt ordering", slug=f"alt-{str(ULID()).lower()}",
        status=ContentStatus.DRAFT,
    )
    db.add(alt)
    await db.flush()
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_COHORT_PATH, domain="learning",
        unit_type="cohort", treatment_config={"alternative_path_id": alt.id},
    )
    cohort_unit = await _treatment_unit(db, exp, "cohort", "coh")
    assert await hooks.cohort_path_override(
        db, cohort_id=cohort_unit, org_id=org.id
    ) == alt.id
    # Cross-org read refused — curricula never leak across orgs
    assert await hooks.cohort_path_override(
        db, cohort_id=cohort_unit, org_id="x" * 26
    ) is None
    assert await _exposures(db, exp.id) == 1


# ── Rubric wording (Part F) ──────────────────────────────────────────


async def test_rubric_override_shape_validated(db):
    good = [{"criterion": "clarity", "max_score": 5}]
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_RUBRIC_WORDING, domain="assessment",
        unit_type="project", treatment_config={"rubric": good},
    )
    project_unit = await _treatment_unit(db, exp, "project", "proj")
    assert await hooks.rubric_override(db, project_id=project_unit) == good
    assert await _exposures(db, exp.id) == 1


async def test_rubric_override_rejects_malformed(db):
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_RUBRIC_WORDING, domain="assessment",
        unit_type="project", treatment_config={"rubric": [{"no_criterion": 1}]},
    )
    project_unit = await _treatment_unit(db, exp, "project", "projm")
    assert await hooks.rubric_override(db, project_id=project_unit) is None
    # defect #37: the fallback IS this unit's exposure (arm recorded)
    assert await _exposures(db, exp.id) == 1


# ── Retry policy (operational) ───────────────────────────────────────


async def test_retry_policy_override_clamped(db):
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_RETRY_POLICY, domain="operational",
        unit_type="tenant", treatment_config={"max_attempts": 99},
    )
    tenant_unit = await _treatment_unit(db, exp, "tenant", "ten")
    assert await hooks.retry_policy_override(db, tenant_id=tenant_unit) == 10  # clamped
    assert await _exposures(db, exp.id) == 1


async def test_retry_policy_non_int_refused(db):
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_RETRY_POLICY, domain="operational",
        unit_type="tenant", treatment_config={"max_attempts": "five"},
    )
    tenant_unit = await _treatment_unit(db, exp, "tenant", "tenx")
    assert await hooks.retry_policy_override(db, tenant_id=tenant_unit) is None


async def test_control_arm_records_exposure_too(db):
    """Exposure must cover BOTH arms at the decision point — a control unit
    hitting the surface records an exposure with the default experience
    (otherwise exposure-based metrics compare treatment-exposed against
    control-never-exposed)."""
    entity_type, _active, candidate = await _mk_matching_pair(db)
    # control-heavy: resolved units are control with p=.9999
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_MATCHING_CONFIG, domain="matching",
        unit_type="organization",
        treatment_config={"matching_config_id": candidate.id},
        control_weight_bp=9999,
    )
    asvc = AssignmentService(db)
    control_unit = None
    for i in range(20):
        r = await asvc.resolve(
            experiment_key=exp.key, unit_type="organization", unit_id=f"ctl-{i}"
        )
        if r is not None and r.variant_key == "control":
            control_unit = f"ctl-{i}"
            break
    assert control_unit, "no control unit in 20 probes (p < 1e-60)"
    before = await _exposures(db, exp.id)
    result = await hooks.matching_config_override(
        db, org_id=control_unit, target_entity_type=entity_type
    )
    assert result is None  # control serves the default experience
    assert await _exposures(db, exp.id) == before + 1  # ...but IS exposed


async def test_exposures_dedup_per_unit_per_day(db):
    """A unit hitting the surface repeatedly in one UTC day records exactly
    ONE exposure row (table-growth bomb class) — and the exposure_rate source
    counts DISTINCT units, so the rate can never exceed 1.0."""
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_RETRY_POLICY, domain="operational",
        unit_type="tenant", treatment_config={"max_attempts": 5},
    )
    tenant_unit = await _treatment_unit(db, exp, "tenant", "dedup")
    for _ in range(4):
        assert await hooks.retry_policy_override(db, tenant_id=tenant_unit) == 5
    assert await _exposures(db, exp.id) == 1
    # exposure_rate over the day window: distinct units / assigned <= 1.0
    from datetime import UTC, datetime, time, timedelta

    from app.experiments.services.metrics import MetricService

    start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=start, window_end=start + timedelta(days=1)
    )
    snapshots = await MetricService(db).list_snapshots(exp.id, metric_key="exposure_rate")
    for s in snapshots:
        if s.denominator:
            assert float(s.numerator) / float(s.denominator) <= 1.0


async def test_negative_cache_invalidated_on_create(db):
    """resolve() on a missing key negative-caches it; creating an experiment
    with that key must take effect immediately in-process."""
    from app.experiments.services.assignment import forget_missing_key

    key = f"surface-cache-{str(ULID()).lower()[-8:]}"
    forget_missing_key(key)
    asvc = AssignmentService(db)
    assert await asvc.resolve(experiment_key=key, unit_type="user", unit_id="u1") is None
    # key now negative-cached; creating the experiment must invalidate it
    exp, _ = await _mk_surface_experiment(
        db, key=key, domain="marketplace", unit_type="user",
        treatment_config={"sort": "most_installed"},
    )
    resolved = await asvc.resolve(experiment_key=key, unit_type="user", unit_id="u1")
    assert resolved is not None


# ── Fail-safe: no experiment on a surface = pure control ─────────────


async def test_hooks_are_noops_without_experiments(db):
    assert await hooks.matching_config_override(
        db, org_id="o" * 26, target_entity_type="workflow_pack"
    ) is None
    assert await hooks.registry_sort_override(db, user_id="u" * 26) is None
    assert await hooks.cohort_path_override(db, cohort_id="c" * 26, org_id="o" * 26) is None
    assert await hooks.rubric_override(db, project_id="p" * 26) is None
    assert await hooks.retry_policy_override(db, tenant_id="t" * 26) is None


async def test_fallback_exposure_context_pins_the_arm(db):
    """Defect #37 detail pin: the invalid-override fallback exposure carries
    arm=fallback — distinguishable from control and treatment exposures in
    the funnel and in debugging."""
    from sqlalchemy import select as _select

    exp, _admin = await _mk_surface_experiment(
        db, key="surface-registry-ordering", domain="marketplace",
        unit_type="user", treatment_config={"sort": "no-such-sort-strategy"},
    )
    from app.experiments.hooks import registry_sort_override

    unit = await _treatment_unit(db, exp, "user", "fbk")
    result = await registry_sort_override(db, user_id=unit)
    assert result is None
    row = (
        await db.execute(
            _select(ExperimentExposure).where(ExperimentExposure.experiment_id == exp.id)
        )
    ).scalar_one()
    assert row.context["arm"] == "fallback"


async def test_binding_override_inactive_offering_falls_back(db):
    """Mutation-killer (round 19): an offering that EXISTS but is inactive
    must fall back on its own — an Or→And flip there would let a deactivated
    credentialed offering keep serving an experiment override."""
    org, offering = await _mk_offering(db, capability="text.generate", active=False)
    exp, _ = await _mk_surface_experiment(
        db, key=hooks.SURFACE_WORKFLOW_BINDING, domain="workflow",
        unit_type="workflow_installation",
        treatment_config={"offering_id": offering.id},
    )
    install_unit = await _treatment_unit(db, exp, "workflow_installation", "instx")
    assert await hooks.workflow_binding_override(
        db, installation_id=install_unit, org_id=org.id,
        capability="text.generate", required_features=set(),
    ) is None
    assert await _exposures(db, exp.id) == 1  # arm=fallback recorded
