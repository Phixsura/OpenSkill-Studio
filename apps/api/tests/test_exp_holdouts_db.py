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


async def _mk_running(
    db, *, domain: str = "learning", layer_key: str | None = None,
    spec_overrides: dict | None = None,
):
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
    await svc.create_version(exp.id, spec=_spec(**(spec_overrides or {})), actor=admin)
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
    assert exc.value.status_code == 422
    # bp boundaries: 1 and the max are legal; 0 is not
    ok_low = await svc.create(key=f"hg-{str(ULID()).lower()}", title="lo",
                              domain="learning", holdout_bp=1)
    assert ok_low.holdout_bp == 1
    ok_high = await svc.create(key=f"hg-{str(ULID()).lower()}", title="hi",
                               domain="learning", holdout_bp=2000)
    assert ok_high.holdout_bp == 2000
    with pytest.raises(AppError) as exc:
        await svc.create(key="hg-zero", title="x", domain="learning", holdout_bp=0)
    assert exc.value.code == "EXPERIMENT_HOLDOUT_BP_INVALID"
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
    assert exc.value.status_code == 404


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


async def test_holdout_group_cache_actually_caches(db):
    """The 60s domain cache must serve the second lookup without a DB round
    trip (a from-now-MINUS-ttl expiry would silently disable it)."""
    from app.experiments.services.holdouts import active_holdout_groups

    await HoldoutGroupService(db).create(
        key=f"hg-{str(ULID()).lower()}", title="c", domain="learning", holdout_bp=100
    )
    first = await active_holdout_groups(db, "learning")
    assert len(first) >= 1
    calls = {"n": 0}
    real_execute = db.execute

    async def counting_execute(*args, **kwargs):
        calls["n"] += 1
        return await real_execute(*args, **kwargs)

    db.execute = counting_execute  # type: ignore[method-assign]
    try:
        second = await active_holdout_groups(db, "learning")
    finally:
        db.execute = real_execute  # type: ignore[method-assign]
    assert second == first
    assert calls["n"] == 0  # served from cache


async def test_interaction_alert_detail_and_min_boundary(db):
    """Pins: df is (r-1)(c-1)=1 for 2x2, exactly one alert per pair per
    sweep, and EXACTLY 100 shared units (the minimum) is enough."""
    from app.experiments.worker import sweep_experiment_interactions

    exp1, exp2 = await _mk_pair_with_shared_units(db, correlated=True, n=100)
    alerts = await sweep_experiment_interactions(db, cap_pairs=500)
    assert alerts == 1
    event = (
        await db.execute(
            select(GuardrailEvent).where(
                GuardrailEvent.experiment_id == exp1.id,
                GuardrailEvent.guardrail_key == INTERACTION_GUARDRAIL_KEY,
            )
        )
    ).scalar_one()
    assert event.detail["df"] == 1
    assert event.detail["shared_units"] == 100
    assert event.detail["with"] == exp2.id


# Verified-equivalent mutation survivors (ledger):
# - cache TTL `>` vs `>=` and ends_at `>` vs `>=`: exact-instant boundaries,
#   measure zero on real clocks.
# - interaction `expected <= 0`: row/col totals of observed keys are always
#   positive — defensive edge.
# - `chi2_sf >= 0.001` and the 7-day `>=`: exact-boundary equivalents.
# - round(chi2, 3→4): fully-correlated tables give integer chi2.


async def test_org_admin_write_delegation_transition_and_ramp(db):
    """Write delegation (§18): an org admin transitions and ramps THEIR org's
    experiment; a platform experiment is a uniform 404; the decision runtime
    gate still refuses direct promotion for every caller."""
    from app.experiments.api.deps import experiment_read_scope
    from app.experiments.services.experiments import ExperimentService

    org_admin, org = await _mk_org_admin(db)
    platform_exp, admin = await _mk_running(db)
    svc = ExperimentService(db)
    layer_key = platform_exp.layer_key
    org_exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="Org-run", domain="learning",
        layer_key=layer_key, owner_user_id=admin.id, scope_org_id=org.id,
    )
    await svc.create_version(org_exp.id, spec=_spec(), actor=org_admin)

    scope = await experiment_read_scope(user=org_admin, db=db)
    # own-org experiment: the full operating path works under the org admin
    await svc.get_scoped(org_exp.id, scope.org_ids)
    await svc.transition(org_exp.id, to_status="review", actor=org_admin)
    row = await svc.get(org_exp.id)
    assert row.status == "review"

    # platform experiment: uniform 404 BEFORE any transition runs
    with pytest.raises(AppError) as e:
        await svc.get_scoped(platform_exp.id, scope.org_ids)
    assert e.value.status_code == 404
    assert (await svc.get(platform_exp.id)).status == "running"  # untouched

    # the no-auto-promote posture holds for delegated writers too
    with pytest.raises(AppError) as e:
        await svc.transition(org_exp.id, to_status="promoted", actor=org_admin)
    # blocked either by the state machine (review cannot promote) or, from an
    # analyzable state, by the decision runtime gate — never allowed
    assert e.value.code in ("EXPERIMENT_INVALID_TRANSITION", "EXPERIMENT_DECISION_REQUIRED")


async def test_holdout_group_org_scoped_applies_to_org_experiments(db):
    """The symmetric face: an org-scoped group DOES withhold members from
    that org's own experiments (only platform experiments are exempt)."""
    from app.controlplane.models.tenant import TenantAccount
    from app.models.organization import Organization

    tenant = TenantAccount(name=f"t-{str(ULID()).lower()}", slug=f"t-{str(ULID()).lower()}")
    db.add(tenant)
    await db.flush()
    org = Organization(name="hg sym", slug=f"hg-{str(ULID()).lower()}", tenant_id=tenant.id)
    db.add(org)
    await db.flush()
    platform_exp, admin = await _mk_running(db)
    svc = ExperimentService(db)
    layer2 = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="learning"
    )
    org_exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="OrgScoped", domain="learning",
        layer_key=layer2.key, owner_user_id=admin.id, scope_org_id=org.id,
    )
    await svc.create_version(org_exp.id, spec=_spec(), actor=admin)
    await LayerService(db).allocate(
        layer_key=layer2.key, experiment_id=org_exp.id, slice_start=0, slice_end=9999,
    )
    group = await HoldoutGroupService(db).create(
        key=f"hg-{str(ULID()).lower()}", title="org hold", domain="learning",
        holdout_bp=2000, scope_org_id=org.id,
    )
    member, _ = _member_and_nonmember(group.key, 2000)
    preview = await AssignmentService(db).compute(
        experiment=org_exp, unit_type="user", unit_id=member,
        context={"org_id": org.id},
    )
    assert preview["eligible"] is False
    assert preview.get("holdout_group") == group.key


async def test_holdout_group_concurrent_create_same_key_races_to_409(db):
    """Defect #33 (R88 class): two committed sessions racing the same key —
    one wins, the loser gets the TYPED 409 (the pre-check select alone has a
    race window that used to surface an unmapped IntegrityError)."""
    import asyncio

    from sqlalchemy import delete

    key = f"hg-race-{str(ULID()).lower()}"

    async def _create():
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            try:
                await HoldoutGroupService(session).create(
                    key=key, title="race", domain="learning", holdout_bp=100
                )
                await session.commit()
                return "created"
            except AppError as exc:
                return exc.code

    try:
        results = await asyncio.gather(_create(), _create())
        assert sorted(results) == ["EXPERIMENT_HOLDOUT_KEY_TAKEN", "created"], results
    finally:
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            await session.execute(delete(HoldoutGroup).where(HoldoutGroup.key == key))
            await session.commit()


async def test_holdout_key_reusable_after_release(db):
    """Defect #34 (the round-3 one-shot-key lesson, holdout edition): a
    released group frees its key for a NEW group; two ACTIVE same-key groups
    stay impossible."""
    svc = HoldoutGroupService(db)
    key = f"hg-{str(ULID()).lower()}"
    first = await svc.create(key=key, title="first", domain="learning", holdout_bp=100)
    await svc.release(first.id)
    second = await svc.create(key=key, title="second", domain="learning", holdout_bp=200)
    assert second.id != first.id
    assert second.status == "active"
    with pytest.raises(AppError) as exc:
        await svc.create(key=key, title="third", domain="learning", holdout_bp=300)
    assert exc.value.code == "EXPERIMENT_HOLDOUT_KEY_TAKEN"
    # exclusion follows the ACTIVE group's band (200bp, not the released 100)
    member, _ = _member_and_nonmember(key, 200)
    exp, _admin = await _mk_running(db)
    preview = await AssignmentService(db).compute(
        experiment=exp, unit_type="user", unit_id=member
    )
    assert preview["eligible"] is False
    assert preview["holdout_group"] == key


async def test_org_admin_delegation_covers_snapshots_and_analysis(db):
    """Delegation consistency: an org admin who can OPERATE their experiment
    can also read its snapshots and run its analysis; platform experiments
    stay a uniform 404 on those surfaces too."""
    from app.experiments.api.deps import experiment_read_scope
    from app.experiments.services.experiments import ExperimentService

    org_admin, org = await _mk_org_admin(db)
    platform_exp, admin = await _mk_running(db)
    svc = ExperimentService(db)
    scope = await experiment_read_scope(user=org_admin, db=db)
    # the scoped gate both analysis and metrics endpoints now share:
    with pytest.raises(AppError) as e:
        await svc.get_scoped(platform_exp.id, scope.org_ids)
    assert e.value.status_code == 404
    layer2 = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="learning")
    org_exp = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="OwnAnalysis", domain="learning",
        layer_key=layer2.key, owner_user_id=admin.id, scope_org_id=org.id,
    )
    assert (await svc.get_scoped(org_exp.id, scope.org_ids)).id == org_exp.id


async def test_platform_admin_dep_direct(db):
    """Direct pin on require_platform_admin: admin passes, non-admin gets
    exactly FORBIDDEN/403 (the mutation lane's dep-flip killer)."""
    from app.experiments.api.deps import require_platform_admin

    admin = await _mk_admin(db)
    assert (await require_platform_admin(user=admin)) is admin
    student = User(
        email=f"dep-{ULID()}@example.com", display_name="S",
        role=UserRole.STUDENT, status=UserStatus.ACTIVE,
    )
    db.add(student)
    await db.flush()
    with pytest.raises(AppError) as e:
        await require_platform_admin(user=student)
    assert e.value.code == "FORBIDDEN"
    assert e.value.status_code == 403


async def test_list_experiments_filters_and_cursor_scope(db):
    """List semantics pinned: status/domain filters are EQUALITY, the cursor
    is strictly-less-than (R395: predicate matches the sort), and
    next_cursor appears exactly when a full page returned."""
    from app.experiments.services.experiments import ExperimentService

    exp1, admin = await _mk_running(db)                       # learning, running
    svc = ExperimentService(db)
    ops_layer = await LayerService(db).create(
        key=f"lyr-{str(ULID()).lower()}", domain="operational"
    )
    draft = await svc.create(
        key=f"exp-{str(ULID()).lower()}", title="Draft", domain="operational",
        layer_key=ops_layer.key, owner_user_id=admin.id,
    )
    rows, total, _ = await svc.list_experiments(status="running")
    assert all(r.status == "running" for r in rows)
    assert exp1.id in {r.id for r in rows}
    assert draft.id not in {r.id for r in rows}
    rows, _, _ = await svc.list_experiments(domain="operational")
    domains = {r.domain for r in rows}
    assert domains == {"operational"} or domains == set()
    assert draft.id in {r.id for r in rows}

    # cursor strictly less-than: paging from the NEWER row excludes it
    newer, older = sorted([exp1.id, draft.id], reverse=True)
    rows, _, _ = await svc.list_experiments(cursor=newer, limit=500)
    ids = {r.id for r in rows}
    assert newer not in ids
    assert older in ids

    # next_cursor exactly when the page is full
    rows, _, next_cursor = await svc.list_experiments(limit=1)
    assert len(rows) == 1 and next_cursor == rows[-1].id
    rows, _, next_cursor = await svc.list_experiments(limit=100000)
    assert next_cursor is None


# Wave-5 survivor ledger: ExperimentService.list_experiments' limit default
# (50) is unreachable — the API layer always passes an explicit Query-bound
# limit; the default exists only for internal callers.


async def test_holdout_group_excludes_switchback_enrollment_too(db):
    """Combination: a domain holdout group withholds members from SWITCHBACK
    experiments exactly like parallel ones (the group check precedes the
    design branch in compute)."""
    exp, _ = await _mk_running(
        db,
        spec_overrides={
            "design": "switchback",
            "switchback": {"switch_unit": "platform_day", "window_minutes": 1440},
        },
    )
    group = await HoldoutGroupService(db).create(
        key=f"hg-{str(ULID()).lower()}", title="sb hold", domain="learning",
        holdout_bp=2000,
    )
    member, nonmember = _member_and_nonmember(group.key, 2000)
    svc = AssignmentService(db)
    assert await svc.resolve(
        experiment_key=exp.key, unit_type="user", unit_id=member
    ) is None
    served = await svc.resolve(
        experiment_key=exp.key, unit_type="user", unit_id=nonmember
    )
    assert served is not None and served.variant_key in ("control", "treatment")
