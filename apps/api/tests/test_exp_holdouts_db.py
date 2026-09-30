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


# ── Org-admin read delegation (v2 batch 7, §18) ──────────────────────


async def _mk_org_admin(db):
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization, OrgMember, OrgRole

    user = User(
        email=f"orgadm-{ULID()}@example.com", display_name="OA",
        role=UserRole.STUDENT, status=UserStatus.ACTIVE,
    )
    db.add(user)
    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}", slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(
        name="delegated", slug=f"d-{str(ULID()).lower()}", tenant_id=tenant.id
    )
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.ADMIN))
    await db.flush()
    return user, org


async def test_org_admin_read_scope_filters_and_uniform_404(db):
    """An org admin reads ONLY experiments scoped to their orgs; a platform
    experiment is a uniform 404 (no existence oracle) and the list never
    shows it. A user with no org-admin role gets 403."""
    from app.experiments.api.deps import experiment_read_scope
    from app.experiments.services.experiments import ExperimentService

    org_admin, org = await _mk_org_admin(db)
    platform_exp, admin = await _mk_running(db)
    svc = ExperimentService(db)
    org_exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="Org exp", domain="learning",
        layer_key=platform_exp.layer_key, owner_user_id=admin.id,
        scope_org_id=org.id,
    )

    scope = await experiment_read_scope(user=org_admin, db=db)
    assert scope.org_ids == [org.id]

    rows, total, _cursor = await svc.list_experiments(scope_org_ids=scope.org_ids)
    ids = {r.id for r in rows}
    assert org_exp.id in ids
    assert platform_exp.id not in ids
    assert total == len(ids)

    # scoped get: own org experiment readable; platform experiment = 404
    got = await svc.get_scoped(org_exp.id, scope.org_ids)
    assert got.id == org_exp.id
    with pytest.raises(AppError) as e:
        await svc.get_scoped(platform_exp.id, scope.org_ids)
    assert e.value.code == "EXPERIMENT_NOT_FOUND"
    assert e.value.status_code == 404

    # platform admin scope is unrestricted
    admin_scope = await experiment_read_scope(user=admin, db=db)
    assert admin_scope.org_ids is None
    assert (await svc.get_scoped(platform_exp.id, None)).id == platform_exp.id

    # no org-admin role anywhere → 403, not an empty allow-list
    nobody = User(
        email=f"nobody-{ULID()}@example.com", display_name="N",
        role=UserRole.STUDENT, status=UserStatus.ACTIVE,
    )
    db.add(nobody)
    await db.flush()
    with pytest.raises(AppError) as e:
        await experiment_read_scope(user=nobody, db=db)
    assert e.value.code == "FORBIDDEN"
    assert e.value.status_code == 403


async def test_interaction_pair_cap_rotates_weekly(db):
    """§106.26 fairness (defect #30): with more cross-layer pairs than the
    cap, different ISO weeks inspect DIFFERENT pairs — a fixed-order cap
    would starve the tail forever."""
    from datetime import UTC, datetime

    from app.experiments.worker import sweep_experiment_interactions

    # three experiments in three layers → 3 cross-layer pairs; cap = 1
    exps = [await _mk_running(db) for _ in range(3)]
    for exp, _admin in exps:
        for i in range(120):
            db.add(
                ExperimentAssignment(
                    experiment_id=exp.id, unit_type="user", unit_id=f"r{i:024d}",
                    variant_key="control" if i % 2 == 0 else "treatment",
                    assigned_version=1, bucket=0, is_holdout=False,
                )
            )
    await db.flush()
    # fully-correlated shared rosters → every inspected pair alerts; which
    # experiments got events tells us which pair the week's window covered
    seen_pairs = set()
    for week_day in (datetime(2026, 1, 5, tzinfo=UTC),   # ISO week 2
                     datetime(2026, 1, 12, tzinfo=UTC),  # ISO week 3
                     datetime(2026, 1, 19, tzinfo=UTC)):  # ISO week 4
        await sweep_experiment_interactions(db, cap_pairs=1, now=week_day)
        events = list(
            (
                await db.execute(
                    select(GuardrailEvent).where(
                        GuardrailEvent.guardrail_key == "__interaction__",
                        GuardrailEvent.experiment_id.in_([e.id for e, _a in exps]),
                    )
                )
            ).scalars()
        )
        pair = frozenset(
            (ev.experiment_id, ev.detail["with"]) for ev in events
        )
        seen_pairs.add(pair)
        # reset for the next simulated week
        for ev in events:
            await db.delete(ev)
        await db.flush()
    assert len(seen_pairs) == 3  # every week inspected a different pair
