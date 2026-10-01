"""Experiments facade — the ONLY entry point for product code (ADR-017 §7).

Product code (learning paths, evaluation, workflow runtime, matching,
registry) imports ONLY from this module. Fail-safe posture: a resolution
failure returns None (control experience) and logs — an experiment must
never crash a product path. Configs returned here still pass ALL of the
target domain's own validations and approval gates (R79/R82/R83).
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.experiments.services.assignment import AssignmentService, ResolvedVariant

logger = structlog.get_logger()


async def resolve_variant(
    db: AsyncSession,
    *,
    experiment_key: str,
    unit_type: str,
    unit_id: str,
    context: dict | None = None,
) -> ResolvedVariant | None:
    """Sticky deterministic assignment; None means: serve the control/default
    experience (ineligible, not ramped, holdout, paused, or unknown key)."""
    try:
        # Defect #41: the service call runs under a SAVEPOINT. A mid-flush DB
        # error would otherwise poison the HOST's session (PendingRollback) —
        # the damage surfacing later at the host's own commit, OUTSIDE every
        # shield, breaking the product write the experiment rode along with.
        # The savepoint rollback discards only the experiment writes; the
        # host's prior uncommitted business writes stay intact.
        async with db.begin_nested():
            return await AssignmentService(db).resolve(
                experiment_key=experiment_key,
                unit_type=unit_type,
                unit_id=unit_id,
                context=context,
            )
    except Exception:  # noqa: BLE001 — experiments never break product paths
        logger.warning(
            "experiment_resolve_failed", experiment_key=experiment_key, unit_type=unit_type
        )
        return None


async def record_exposure(
    db: AsyncSession,
    *,
    experiment_key: str,
    unit_type: str,
    unit_id: str,
    dedup_key: str | None = None,
    context: dict | None = None,
) -> bool:
    """Append-only exposure at the moment the variant takes effect."""
    try:
        async with db.begin_nested():  # defect #41 — see resolve_variant
            return await AssignmentService(db).record_exposure(
                experiment_key=experiment_key,
                unit_type=unit_type,
                unit_id=unit_id,
                dedup_key=dedup_key,
                context=context,
            )
    except Exception:  # noqa: BLE001 — exposures never break product paths
        logger.warning(
            "experiment_exposure_failed", experiment_key=experiment_key, unit_type=unit_type
        )
        return False
