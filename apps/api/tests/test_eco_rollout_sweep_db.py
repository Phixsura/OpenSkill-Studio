"""Round-28 tests (ADR-016 §36): automatic rollout evaluation sweep."""

import pytest
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.ecosystem.services.replacement import ReplacementService
from app.ecosystem.services.rollout import RolloutService
from app.ecosystem.worker import sweep_rollout_evaluations
from app.models.notification import Notification
from tests.test_eco_services_db import _mk_model_version, _mk_user


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def test_sweep_evaluates_running_plans_and_stays_hands_off(db):
    admin = await _mk_user(db, "admin")
    deprecated = await _mk_model_version(db, "SweepOld")
    await _mk_model_version(db, "SweepNew")
    ranked, _ = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    svc = RolloutService(db)
    plan = await svc.create(
        replacement_candidate_id=ranked[0].id, scope_type="benchmark_only"
    )
    await svc.start(plan.id)

    out = await sweep_rollout_evaluations(db)
    assert out["evaluated"] == 1
    await db.refresh(plan)
    # Evaluated, comparison stored — but NEVER promoted/rolled back by the sweep
    assert plan.status == "evaluating"
    assert plan.comparison is not None
    # No regressions here (no guardrails set) → no admin alert
    assert out["alerted"] == 0
    notes = list(await db.scalars(
        select(Notification).where(
            Notification.user_id == admin.id,
            Notification.type == "ecosystem_rollout_guardrail",
        )
    ))
    assert notes == []

    # Sweep is re-runnable; terminal plans are ignored
    await svc.decide(plan.id, decision="reject", actor_id=admin.id)
    out2 = await sweep_rollout_evaluations(db)
    assert out2["evaluated"] == 0

async def test_guardrail_alert_fires_once_per_regression_set(db, monkeypatch):
    """Mutation-audit killer: the same regression set alerts admins ONCE —
    the fingerprint stamp suppresses re-alerts on every later sweep."""
    from sqlalchemy import select as _select

    from app.ecosystem.services import rollout as rollout_mod
    from app.ecosystem.worker import sweep_rollout_evaluations
    from app.models.notification import Notification

    admin = await _mk_user(db, "admin")
    deprecated = await _mk_model_version(db, "AlertOld")
    await _mk_model_version(db, "AlertNew")
    ranked, _ = await ReplacementService(db).generate_candidates(
        deprecated_kind="model_version", deprecated_id=deprecated.id
    )
    svc = RolloutService(db)
    plan = await svc.create(
        replacement_candidate_id=ranked[0].id, scope_type="benchmark_only"
    )
    await svc.start(plan.id)

    real_evaluate = rollout_mod.RolloutService.evaluate

    async def evaluate_with_regression(self, plan_id):
        plan = await real_evaluate(self, plan_id)
        plan.comparison = {**(plan.comparison or {}), "regressions": ["speed_p50_ms"]}
        return plan

    monkeypatch.setattr(rollout_mod.RolloutService, "evaluate", evaluate_with_regression)
    out1 = await sweep_rollout_evaluations(db)
    assert out1["alerted"] == 1
    out2 = await sweep_rollout_evaluations(db)
    assert out2["alerted"] == 0  # same regression set never re-alerts
    notes = list(await db.scalars(
        _select(Notification).where(
            Notification.user_id == admin.id,
            Notification.type == "ecosystem_rollout_guardrail",
        )
    ))
    assert len(notes) == 1
