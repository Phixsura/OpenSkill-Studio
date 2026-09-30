"""Full experimentation E2E (issue #42 acceptance criteria).

Hypothesis → design (immutable spec) → layer allocation → schedule → run →
deterministic sticky assignment → exposure → outbox-driven snapshots →
guardrail evaluation (clean) → complete → analyze (looks + result hash) →
human promote decision (hash-gated) → promotion draft → approve → apply →
the target domain holds its own DRAFT object (inactive MatchingConfig
version) and the whole trail is auditable.

Service-level E2E against the dev Postgres; rolls back at the end.
"""

from datetime import UTC, datetime, time, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.worker import process_outbox_once
from app.core.database import AsyncSessionLocal
from app.exceptions import AppError
from app.experiments import facade, hooks
from app.experiments.models import ExperimentEvent, MetricSnapshot
from app.experiments.security import ETHICS_CHECKLIST_KEY, LAUNCH_CHECKLIST_KEYS
from app.experiments.services.analysis_service import AnalysisService
from app.experiments.services.decisions import DecisionService
from app.experiments.services.experiments import ExperimentService
from app.experiments.services.guardrails import GuardrailService
from app.experiments.services.layers import LayerService
from app.experiments.services.metrics import MetricService
from app.experiments.services.promotion import PromotionService
from app.experiments.worker import sweep_experiment_windows
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


async def test_full_lifecycle_hypothesis_to_controlled_promotion(db):
    """NOTE: process_outbox_once COMMITS mid-test (its claim/ack phases), so
    the rollback fixture cannot undo this test — residue is deleted up front
    (idempotent self-heal) and again in the finally cleanup (§106.25)."""
    from sqlalchemy import delete

    from app.experiments.models import Experiment

    await db.execute(
        delete(Experiment).where(Experiment.key == hooks.SURFACE_MATCHING_CONFIG)
    )
    # ── 0 · Actors & target-domain baseline ──────────────────────────
    admin = User(
        email=f"exp-e2e-{ULID()}@example.com", display_name="Operator",
        role=UserRole.ADMIN, status=UserStatus.ACTIVE,
    )
    db.add(admin)
    await db.flush()
    entity_type = f"exp-{str(ULID()).lower()[-10:]}"
    active_config = MatchingConfig(
        version=1, target_entity_type=entity_type,
        weights={"skill_fit": 1.0}, thresholds={}, is_active=True,
    )
    candidate_config = MatchingConfig(
        version=2, target_entity_type=entity_type,
        weights={"skill_fit": 0.6, "history": 0.4}, thresholds={}, is_active=False,
    )
    db.add_all([active_config, candidate_config])
    await MetricService(db).ensure_seed_definitions()

    # ── 1 · Design: immutable spec on a mutual-exclusion layer ───────
    layer = await LayerService(db).create(key=f"lyr-{str(ULID()).lower()}", domain="matching")
    esvc = ExperimentService(db)
    exp = await esvc.create(
        key=hooks.SURFACE_MATCHING_CONFIG,  # controls the matching surface
        title="Alternative matching weights", domain="matching",
        layer_key=layer.key, owner_user_id=admin.id,
    )
    version = await esvc.create_version(
        exp.id,
        spec={
            "hypothesis": "candidate weights improve match acceptance safely",
            "unit_type": "organization",
            "variants": [
                {"key": "control", "name": "Active config", "weight_bp": 5000,
                 "is_control": True},
                {"key": "treatment", "name": "Candidate config", "weight_bp": 5000,
                 "config": {"matching_config_id": candidate_config.id}},
            ],
            "metrics": {
                "primary": ["exposure_rate"],
                "guardrails": [
                    # Both arms record exposures at the decision point, so a
                    # fully-exercised surface legitimately reaches 1.0
                    {"metric_key": "exposure_rate", "op": "lte", "threshold": 1.0,
                     "window_hours": 24}
                ],
            },
            "sequential": "obrien_fleming",
            "stop_policy": {"max_days": 28, "max_looks": 3},
        },
        actor=admin,
    )
    assert version.version == 1 and len(version.spec_hash) == 64
    await LayerService(db).allocate(
        layer_key=layer.key, experiment_id=exp.id, slice_start=0, slice_end=9999
    )

    # ── 2 · Schedule → run → ramp ────────────────────────────────────
    for status in ("review", "scheduled", "running"):
        await esvc.transition(
            exp.id, to_status=status, actor=admin,
            checklist=_CHECKLIST if status == "scheduled" else None,
        )
    await esvc.set_ramp(exp.id, ramp_bp=10_000, actor=admin)

    # ── 3 · Sticky assignment + the REAL matching hook + exposure ────
    org_units = [f"org-{i}" for i in range(30)]
    served: dict[str, str] = {}
    for org in org_units:
        resolved = await facade.resolve_variant(
            db, experiment_key=exp.key, unit_type="organization", unit_id=org
        )
        assert resolved is not None
        served[org] = resolved.variant_key
        # The domain hook applies the candidate config ONLY for treatment
        override = await hooks.matching_config_override(
            db, org_id=org, target_entity_type=entity_type
        )
        if resolved.variant_key == "treatment":
            assert override is not None and override.id == candidate_config.id
        else:
            assert override is None
    assert set(served.values()) == {"control", "treatment"}
    # Stickiness: re-resolution never flips anyone
    for org in org_units:
        again = await facade.resolve_variant(
            db, experiment_key=exp.key, unit_type="organization", unit_id=org
        )
        assert again is not None and again.variant_key == served[org]

    # ── 4 · Snapshots via the outbox worker ──────────────────────────
    enqueued = await sweep_experiment_windows(db)
    assert enqueued >= 1
    await process_outbox_once(db, topics=["exp.compute_snapshots"])
    # Yesterday's window is empty; compute today's directly for the analysis
    start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    await MetricService(db).compute_experiment_window(
        exp.id, window_start=start, window_end=start + timedelta(days=1)
    )
    snapshots = list(
        (
            await db.execute(
                select(MetricSnapshot).where(MetricSnapshot.experiment_id == exp.id)
            )
        ).scalars()
    )
    assert snapshots, "snapshot pipeline produced nothing"

    # ── 5 · Guardrails: clean evaluation, no pause ───────────────────
    summary = await GuardrailService(db).evaluate_experiment(exp.id)
    assert summary["breaches"] == []
    assert (await esvc.get(exp.id)).status == "running"

    # ── 6 · Complete → analyze (look budget + result hash) ───────────
    await esvc.transition(exp.id, to_status="completed", actor=admin)
    await esvc.transition(exp.id, to_status="analyzed", actor=admin)
    analysis = await AnalysisService(db).run(exp.id, actor=admin)
    assert analysis["causal_claim"] is True
    assert analysis["looks"] == {"used": 1, "max": 3}
    result_hash = analysis["result_hash"]

    # ── 7 · Human decision, hash-gated ───────────────────────────────
    with pytest.raises(AppError):  # forged hash refused
        await DecisionService(db).create(
            exp.id, decision="promote", summary="forged evidence must not pass",
            analysis_result_hash="0" * 64, actor=admin,
        )
    record = await DecisionService(db).create(
        exp.id, decision="promote",
        summary="candidate weights won cleanly under guardrails",
        analysis_result_hash=result_hash, actor=admin,
    )
    assert record.guardrail_outcome["clean"] is True
    assert (await esvc.get(exp.id)).status == "promoted"

    # ── 8 · Controlled promotion → target-domain DRAFT object ────────
    psvc = PromotionService(db)
    draft = await psvc.create_draft(
        record.id, target_type="matching_config", target_ref=active_config.id,
        draft_payload={"weights": {"skill_fit": 0.6, "history": 0.4}}, actor=admin,
    )
    await psvc.approve(draft.id, actor=admin)
    applied = await psvc.apply(draft.id, actor=admin)
    new_config = await db.get(MatchingConfig, applied.applied_ref)
    assert new_config.is_active is False  # activation stays a matching call
    assert new_config.version == 3
    assert (await db.get(MatchingConfig, active_config.id)).is_active is True

    # ── 9 · The whole trail is auditable ─────────────────────────────
    events = list(
        (
            await db.execute(
                select(ExperimentEvent.event_type).where(
                    ExperimentEvent.experiment_id == exp.id
                )
            )
        ).scalars()
    )
    for expected in (
        "created", "version_created", "transition", "ramp_changed",
        "analysis_look", "decision_recorded", "promotion_drafted",
    ):
        assert expected in events, f"audit trail missing {expected}"

    # ── 10 · Cleanup: this test COMMITTED (outbox phases) — leave the dev
    # DB as found; a failed run's residue self-heals via the pre-delete.
    from app.experiments.models import ExperimentLayer

    await db.execute(delete(Experiment).where(Experiment.id == exp.id))
    await db.execute(delete(ExperimentLayer).where(ExperimentLayer.key == layer.key))
    await db.execute(
        delete(MatchingConfig).where(MatchingConfig.target_entity_type == entity_type)
    )
    await db.execute(delete(User).where(User.id == admin.id))
    await db.commit()
