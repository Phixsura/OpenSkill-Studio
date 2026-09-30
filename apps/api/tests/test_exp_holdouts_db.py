"""Global holdout groups + cross-experiment interaction sweep (ADR-017 v2
batch 2: §4.12 holdout groups, §4.13 interaction detection).

Runs against the dev Postgres (exp07 applied); rollback-per-test.
"""

import pytest
from sqlalchemy import select
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.exceptions import AppError
from app.experiments.models import (
    Experiment,
    ExperimentAssignment,
    GuardrailEvent,
    HoldoutGroup,
)
from app.experiments.models.guardrail import INTERACTION_GUARDRAIL_KEY
from app.experiments.security import ETHICS_CHECKLIST_KEY, LAUNCH_CHECKLIST_KEYS
from app.experiments.services.assignment import AssignmentService, holdout_group_roll
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.holdouts import (
    HoldoutGroupService,
    invalidate_holdout_group_cache,
)
from app.experiments.services.layers import LayerService
from app.models.user import User, UserRole, UserStatus

_CHECKLIST = {key: True for key in (*LAUNCH_CHECKLIST_KEYS, ETHICS_CHECKLIST_KEY)}


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        invalidate_holdout_group_cache()
        yield session
        await session.rollback()
    invalidate_holdout_group_cache()
    await engine.dispose()


def _spec(**overrides) -> dict:
    base = {
        "hypothesis": "treatment improves the primary metric safely",
        "unit_type": "user",
        "variants": [
            {"key": "control", "name": "Control", "weight_bp": 5000, "is_control": True},
            {"key": "treatment", "name": "Treatment", "weight_bp": 5000},
        ],
        "metrics": {
            "primary": ["project_approval_rate"],
            "guardrails": [{"metric_key": "cost_usd", "op": "lte", "threshold": 100.0}],
        },
    }
    base.update(overrides)
    return base


async def _mk_admin(db) -> User:
    user = User(
        email=f"exp-admin-{ULID()}@example.com",
        display_name="Exp Admin",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_running(db, *, domain: str = "learning", layer_key: str | None = None):
    admin = await _mk_admin(db)
    layer_key = layer_key or f"lyr-{str(ULID()).lower()}"
    layer = await LayerService(db).create(key=layer_key, domain=domain)
    svc = ExperimentService(db)
    exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}",
        title="T",
        domain=domain,
        layer_key=layer.key,
        owner_user_id=admin.id,
    )
    await svc.create_version(exp.id, spec=_spec(), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )
    await svc.transition(exp.id, to_status="review", actor=admin)
    await svc.transition(exp.id, to_status="scheduled", actor=admin, checklist=_CHECKLIST)
    await svc.transition(exp.id, to_status="running", actor=admin)
    await svc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)
    return exp, admin


def _member_and_nonmember(group_key: str, bp: int) -> tuple[str, str]:
    """Deterministic unit ids inside/outside a group's band."""
    member = nonmember = None
    i = 0
    while member is None or nonmember is None:
        uid = f"u{i:025d}"
        if holdout_group_roll(group_key, "user", uid) < bp:
            member = member or uid
        else:
            nonmember = nonmember or uid
        i += 1
    return member, nonmember


# ── Holdout group service contract ───────────────────────────────────


async def test_holdout_group_create_validate_and_release(db):
    svc = HoldoutGroupService(db)
    group = await svc.create(key=f"hg-{str(ULID()).lower()}", title="Q4 holdout",
                             domain="learning", holdout_bp=500)
    assert group.status == "active"

    with pytest.raises(AppError) as exc:
        await svc.create(key="hg-bad-domain", title="x", domain="nope", holdout_bp=100)
    assert exc.value.code == "EXPERIMENT_DOMAIN_INVALID"
    with pytest.raises(AppError) as exc:
        await svc.create(key="hg-bad-bp", title="x", domain="learning", holdout_bp=2001)
    assert exc.value.code == "EXPERIMENT_HOLDOUT_BP_INVALID"
    assert exc.value.status_code == 422
    with pytest.raises(AppError) as exc:
        await svc.create(key=group.key, title="dup", domain="learning", holdout_bp=100)
    assert exc.value.code == "EXPERIMENT_HOLDOUT_KEY_TAKEN"
    assert exc.value.status_code == 409
    # bogus org → uniform 404, not FK crash (R89 class)
    with pytest.raises(AppError) as exc:
        await svc.create(key="hg-bad-org", title="x", domain="learning",
                         holdout_bp=100, scope_org_id="0" * 26)
    assert exc.value.status_code == 404

    released = await svc.release(group.id)
    assert released.status == "released"
    assert released.ends_at is not None
    # idempotent
    again = await svc.release(group.id)
    assert again.status == "released"
    with pytest.raises(AppError) as exc:
        await svc.release("0" * 26)
    assert exc.value.code == "EXPERIMENT_HOLDOUT_NOT_FOUND"


# ── Exclusion semantics ──────────────────────────────────────────────


async def test_holdout_group_excludes_new_enrollment_across_domain(db):
    """A member unit is withheld from EVERY experiment in the domain — no
    assignment row is written — while a non-member enrolls normally."""
    exp1, _ = await _mk_running(db)
    exp2, _ = await _mk_running(db)  # different layer, same domain
    group = await HoldoutGroupService(db).create(
        key=f"hg-{str(ULID()).lower()}", title="hold", domain="learning", holdout_bp=1000
    )
    member, nonmember = _member_and_nonmember(group.key, 1000)
    svc = AssignmentService(db)
    for exp in (exp1, exp2):
        assert await svc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=member
        ) is None
        assert await svc.resolve(
            experiment_key=exp.key, unit_type="user", unit_id=nonmember
        ) is not None
    rows = (
        await db.execute(
            select(ExperimentAssignment).where(ExperimentAssignment.unit_id == member)
        )
    ).scalars()
    assert list(rows) == []
    # preview names the group
    preview = await svc.compute(experiment=exp1, unit_type="user", unit_id=member)
    assert preview["eligible"] is False
    assert preview["reason"] == "global holdout group"
    assert preview["holdout_group"] == group.key


async def test_holdout_group_does_not_touch_other_domains(db):
    exp, _ = await _mk_running(db, domain="operational")
    group = await HoldoutGroupService(db).create(
        key=f"hg-{str(ULID()).lower()}", title="hold", domain="learning", holdout_bp=2000
    )
    member, _ = _member_and_nonmember(group.key, 2000)
    resolved = await AssignmentService(db).resolve(
        experiment_key=exp.key, unit_type="user", unit_id=member
    )
    assert resolved is not None


async def test_holdout_group_sticky_assignments_keep_serving(db):
    """Group creation never yanks a served experience — only NEW entry."""
    exp, _ = await _mk_running(db)
    svc = AssignmentService(db)
    group_key = f"hg-{str(ULID()).lower()}"
    member, _ = _member_and_nonmember(group_key, 2000)
    before = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=member)
    assert before is not None
    await HoldoutGroupService(db).create(
        key=group_key, title="hold", domain="learning", holdout_bp=2000
    )
    after = await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=member)
    assert after == before


async def test_holdout_group_release_frees_members(db):
    exp, _ = await _mk_running(db)
    hsvc = HoldoutGroupService(db)
    group = await hsvc.create(
        key=f"hg-{str(ULID()).lower()}", title="hold", domain="learning", holdout_bp=2000
    )
    member, _ = _member_and_nonmember(group.key, 2000)
    svc = AssignmentService(db)
    assert await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=member) is None
    await hsvc.release(group.id)
    assert await svc.resolve(experiment_key=exp.key, unit_type="user", unit_id=member) is not None


async def test_holdout_group_org_scoped_skips_platform_experiments(db):
    """An org-scoped group only withholds from that org's experiments —
    platform-wide experiments (scope_org_id NULL) are untouched."""
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}", slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(
        name="hg org", slug=f"hg-{str(ULID()).lower()}", tenant_id=tenant.id
    )
    db.add(org)
    await db.flush()
    exp, _ = await _mk_running(db)  # platform experiment
    group = await HoldoutGroupService(db).create(
        key=f"hg-{str(ULID()).lower()}", title="org hold", domain="learning",
        holdout_bp=2000, scope_org_id=org.id,
    )
    member, _ = _member_and_nonmember(group.key, 2000)
    resolved = await AssignmentService(db).resolve(
        experiment_key=exp.key, unit_type="user", unit_id=member
    )
    assert resolved is not None


async def test_holdout_group_expired_ends_at_stops_excluding(db):
    from datetime import UTC, datetime, timedelta

    exp, _ = await _mk_running(db)
    group = await HoldoutGroupService(db).create(
        key=f"hg-{str(ULID()).lower()}", title="hold", domain="learning",
        holdout_bp=2000, ends_at=datetime.now(UTC) - timedelta(days=1),
    )
    member, _ = _member_and_nonmember(group.key, 2000)
    assert await AssignmentService(db).resolve(
        experiment_key=exp.key, unit_type="user", unit_id=member
    ) is not None
    row = await db.get(HoldoutGroup, group.id)
    assert row.status == "active"  # expiry needs no status write


async def test_holdout_group_fraction_roughly_matches_bp(db):
    group_key = f"hg-{str(ULID()).lower()}"
    n = 2000
    members = sum(
        1 for i in range(n) if holdout_group_roll(group_key, "user", f"u{i:025d}") < 1000
    )
    assert 0.07 * n < members < 0.13 * n  # 10% ±3pp


# ── Cross-experiment interaction sweep (§4.13) ──────────────────────


async def _mk_pair_with_shared_units(db, *, correlated: bool, n: int = 200):
    """Two running experiments in DIFFERENT layers with n shared units,
    assignments inserted directly to control the contingency table."""
    exp1, _ = await _mk_running(db)
    exp2, _ = await _mk_running(db)
    variants = ("control", "treatment")
    for i in range(n):
        uid = f"s{i:025d}"
        v1 = variants[i % 2]
        # correlated: identical variant; independent: balanced 2x2
        v2 = v1 if correlated else variants[(i // 2) % 2]
        for exp, v in ((exp1, v1), (exp2, v2)):
            db.add(
                ExperimentAssignment(
                    experiment_id=exp.id, unit_type="user", unit_id=uid,
                    variant_key=v, assigned_version=1, bucket=0, is_holdout=False,
                )
            )
    await db.flush()
    return exp1, exp2


async def test_interaction_sweep_alerts_both_sides_and_dedups(db):
    from app.experiments.worker import sweep_experiment_interactions

    exp1, exp2 = await _mk_pair_with_shared_units(db, correlated=True)
    alerts = await sweep_experiment_interactions(db, cap_pairs=500)
    assert alerts >= 1
    await db.flush()
    for exp, other in ((exp1, exp2), (exp2, exp1)):
        events = list(
            (
                await db.execute(
                    select(GuardrailEvent).where(
                        GuardrailEvent.experiment_id == exp.id,
                        GuardrailEvent.guardrail_key == INTERACTION_GUARDRAIL_KEY,
                    )
                )
            ).scalars()
        )
        assert len(events) == 1
        assert events[0].action == "alerted"  # alert-only, never pauses
        assert events[0].detail["with"] == other.id
        assert events[0].detail["shared_units"] == 200
    exp1_row = await db.get(Experiment, exp1.id)
    assert exp1_row.status == "running"
    # 7-day suppression: a second sweep adds nothing for this pair
    again = await sweep_experiment_interactions(db, cap_pairs=500)
    events = list(
        (
            await db.execute(
                select(GuardrailEvent).where(
                    GuardrailEvent.experiment_id == exp1.id,
                    GuardrailEvent.guardrail_key == INTERACTION_GUARDRAIL_KEY,
                )
            )
        ).scalars()
    )
    assert len(events) == 1
    assert again == 0


async def test_interaction_sweep_quiet_on_independent_assignments(db):
    from app.experiments.worker import sweep_experiment_interactions

    exp1, exp2 = await _mk_pair_with_shared_units(db, correlated=False)
    await sweep_experiment_interactions(db, cap_pairs=500)
    events = list(
        (
            await db.execute(
                select(GuardrailEvent).where(
                    GuardrailEvent.experiment_id.in_([exp1.id, exp2.id]),
                    GuardrailEvent.guardrail_key == INTERACTION_GUARDRAIL_KEY,
                )
            )
        ).scalars()
    )
    assert events == []


async def test_interaction_sweep_skips_same_layer_and_small_overlap(db):
    from app.experiments.worker import sweep_experiment_interactions

    # same layer: mutually exclusive by construction — never compared, even
    # with (impossible in production) fully-correlated overlapping rows
    admin_exp1, _ = await _mk_running(db, layer_key=f"lyr-{str(ULID()).lower()}")
    layer_key = admin_exp1.layer_key
    exp2, _ = await _mk_running(db, layer_key=layer_key + "x")
    # small overlap below INTERACTION_MIN_SHARED: quiet
    for i in range(30):
        uid = f"f{i:025d}"
        for exp in (admin_exp1, exp2):
            db.add(
                ExperimentAssignment(
                    experiment_id=exp.id, unit_type="user", unit_id=uid,
                    variant_key="control", assigned_version=1, bucket=0, is_holdout=False,
                )
            )
    await db.flush()
    assert await sweep_experiment_interactions(db, cap_pairs=500) == 0


def test_chi2_sf_wilson_hilferty_accuracy():
    """Pin the WH approximation against the exact alpha=0.001 critical
    values the guardrail table uses — the sweep's gate must agree with the
    table's to within approximation error."""
    from app.experiments.services.analysis import chi2_sf

    for df, crit in ((1, 10.828), (4, 18.467), (9, 27.877)):
        p = chi2_sf(crit, df)
        assert 0.0003 < p < 0.003, (df, p)
    # totality edges
    assert chi2_sf(0.0, 1) == 1.0
    assert chi2_sf(1e6, 1) < 1e-12
    with pytest.raises(ValueError):
        chi2_sf(1.0, 0)


async def test_interaction_sweep_registered_in_cron_table():
    from app.controlplane.worker import _cron_jobs

    assert "exp_interaction_sweep" in {job.name for job in _cron_jobs()}
