"""Domain integration hooks (ADR-017 §7, exp07).

Each product surface has ONE well-known experiment key; creating a running
experiment with that key controls that surface (one live experiment per
surface — layer machinery multiplexes beyond that). Every hook:

- resolves through the fail-safe facade (any error → control experience),
- validates the override under the TARGET DOMAIN'S OWN invariants before
  applying it (R79/R82/R83 gates are never bypassed by an experiment),
- records an exposure only at the moment the override actually takes effect
  (assignment ≠ exposure).

Hard rule (§2.1): no hook exists for consequential employment actions.
"""

from datetime import UTC, datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.experiments import facade


def _dedup_key(unit_type: str, unit_id: str) -> str:
    """One exposure row per unit per UTC day (matches the snapshot windows) —
    without this every surface hit writes a row (table-growth bomb class)."""
    return f"{unit_type}:{unit_id}:{datetime.now(UTC).strftime('%Y%m%d')}"


log = structlog.get_logger()

# Well-known surface keys (experiment.key values)
SURFACE_MATCHING_CONFIG = "surface-matching-config"
SURFACE_WORKFLOW_BINDING = "surface-workflow-binding"
SURFACE_REGISTRY_ORDERING = "surface-registry-ordering"
SURFACE_COHORT_PATH = "surface-cohort-path-structure"
SURFACE_RUBRIC_WORDING = "surface-rubric-wording"
SURFACE_RETRY_POLICY = "surface-workflow-retry-policy"

# Existing registry sort vocabulary — an experiment may only pick among them
REGISTRY_SORTS = frozenset({"newest", "most_installed", "popular", "recently_updated", "name"})

RETRY_ATTEMPTS_MIN, RETRY_ATTEMPTS_MAX = 1, 10



def _shield(fn):
    """Defect #39: the host call sites rely on hooks being TOTAL — but only
    facade.resolve_variant was shielded; the override's own validation
    queries (db.get on configs/offerings/paths) could raise and abort the
    host transaction (an evaluation run, a workflow start, a matching run).
    The whole override is now fail-safe: any exception logs and serves the
    default experience."""
    import functools

    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except Exception:  # noqa: BLE001 — experiments never break product paths
            log.warning("experiment_hook_failed", hook=fn.__name__)
            return None

    return wrapper


async def _expose(
    db: AsyncSession, *, key: str, unit_type: str, unit_id: str, context: dict
) -> None:
    await facade.record_exposure(
        db, experiment_key=key, unit_type=unit_type, unit_id=unit_id,
        dedup_key=_dedup_key(unit_type, unit_id), context=context,
    )


@_shield
async def matching_config_override(
    db: AsyncSession, *, org_id: str, target_entity_type: str
):
    """Part H: controlled test of an alternative (typically still-inactive)
    MatchingConfig version. Soft weights/thresholds only by construction —
    hard eligibility constraints live outside MatchingConfig and are not
    experimentable. Unit: organization."""
    resolved = await facade.resolve_variant(
        db,
        experiment_key=SURFACE_MATCHING_CONFIG,
        unit_type="organization",
        unit_id=org_id,
        context={"org_id": org_id},
    )
    if not resolved:
        return None
    config_id = resolved.config.get("matching_config_id")
    if not config_id:
        # Control arm (or a treatment without an override field): the default
        # experience IS this unit's exposure — record it so the funnel and
        # exposure-based metrics compare like with like (exposure must cover
        # BOTH arms at the decision point).
        await _expose(db, key=SURFACE_MATCHING_CONFIG, unit_type="organization",
                      unit_id=org_id, context={"surface": "matching", "arm": "control"})
        return None
    from app.models.matching import MatchingConfig

    candidate = await db.get(MatchingConfig, config_id)
    # Domain validation: the candidate must target the SAME entity type
    if candidate is None or candidate.target_entity_type != target_entity_type:
        log.warning(
            "experiment_matching_override_invalid",
            config_id=config_id,
            target_entity_type=target_entity_type,
        )
        # Defect #37: a treatment unit falling back to the default is STILL
        # exposed at the decision point — dropping it from the funnel biases
        # exposed-only analysis and false-fires exposure-SRM
        await _expose(db, key=SURFACE_MATCHING_CONFIG, unit_type="organization",
                      unit_id=org_id, context={"surface": "matching", "arm": "fallback"})
        return None
    await _expose(db, key=SURFACE_MATCHING_CONFIG, unit_type="organization",
                  unit_id=org_id, context={"surface": "matching", "config_id": config_id})
    return candidate


@_shield
async def workflow_binding_override(
    db: AsyncSession,
    *,
    installation_id: str | None,
    org_id: str,
    capability: str,
    required_features: set[str],
):
    """Part G: provider/model alternative for a workflow step. The override
    passes the FULL confirmed-rung defense-in-depth (R82): same org, active
    connection, capability match, required features — an experiment never
    exempts the credential path. Unit: workflow_installation."""
    if not installation_id:
        return None
    resolved = await facade.resolve_variant(
        db,
        experiment_key=SURFACE_WORKFLOW_BINDING,
        unit_type="workflow_installation",
        unit_id=installation_id,
    )
    if not resolved:
        return None
    offering_id = resolved.config.get("offering_id")
    if not offering_id:
        await _expose(db, key=SURFACE_WORKFLOW_BINDING, unit_type="workflow_installation",
                      unit_id=installation_id,
                      context={"surface": "workflow_binding", "arm": "control"})
        return None
    from app.models.provider import ProviderConnection, ProviderModelOffering

    offering = await db.get(ProviderModelOffering, offering_id)
    if offering is None or not offering.is_active:
        await _expose(db, key=SURFACE_WORKFLOW_BINDING, unit_type="workflow_installation",
                      unit_id=installation_id,
                      context={"surface": "workflow_binding", "arm": "fallback"})
        return None
    conn = await db.get(ProviderConnection, offering.connection_id)
    if (
        conn is None
        or conn.org_id != org_id
        or conn.status != "active"
        or offering.capability_key != capability
        or not required_features <= set(offering.features or [])
    ):
        log.warning(
            "experiment_binding_override_failed_capability_recheck",
            offering_id=offering_id,
            capability=capability,
        )
        await _expose(db, key=SURFACE_WORKFLOW_BINDING, unit_type="workflow_installation",
                      unit_id=installation_id,
                      context={"surface": "workflow_binding", "arm": "fallback"})
        return None
    await _expose(db, key=SURFACE_WORKFLOW_BINDING, unit_type="workflow_installation",
                  unit_id=installation_id, context={"surface": "workflow_binding", "offering_id": offering_id})
    return offering


@_shield
async def registry_sort_override(db: AsyncSession, *, user_id: str) -> str | None:
    """Marketplace presentation: ordering strategy for the registry list —
    only among the EXISTING sort vocabulary. Unit: user (anonymous visitors
    are never enrolled — identity resolution is out of scope).

    Defect #40: the registry search is a READ-path host — its request
    session is never committed, so sticky assignments and exposures written
    through it were silently discarded at request end (the experiment looked
    live but collected NOTHING). The hook runs its writes in its OWN short
    transaction; the host `db` parameter stays for signature stability."""
    del db  # read-path host session must not carry experiment writes
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as own:
        resolved = await facade.resolve_variant(
            own,
            experiment_key=SURFACE_REGISTRY_ORDERING,
            unit_type="user",
            unit_id=user_id,
        )
        if not resolved:
            await own.commit()  # the sticky assignment may still have landed
            return None
        sort = resolved.config.get("sort")
        if sort is None:
            await _expose(own, key=SURFACE_REGISTRY_ORDERING, unit_type="user",
                          unit_id=user_id,
                          context={"surface": "registry", "arm": "control"})
            await own.commit()
            return None
        if sort not in REGISTRY_SORTS:
            await _expose(own, key=SURFACE_REGISTRY_ORDERING, unit_type="user",
                          unit_id=user_id,
                          context={"surface": "registry", "arm": "fallback"})
            await own.commit()
            return None
        await _expose(own, key=SURFACE_REGISTRY_ORDERING, unit_type="user",
                      unit_id=user_id, context={"surface": "registry", "sort": sort})
        await own.commit()
        return sort


@_shield
async def cohort_path_override(
    db: AsyncSession, *, cohort_id: str, org_id: str
) -> str | None:
    """Part F: alternative learning-path structure for a cohort. The
    alternative must be a real path in the SAME org (may be a draft produced
    by a promotion — that is the controlled exposure of a candidate).
    Recommendations never silently rewrite active curricula: the assigned
    path rows are untouched; only this cohort's effective read is redirected.
    Unit: cohort."""
    # Defect #40: the cohort-path read is also an uncommitted read-path host
    del db
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as own:
        resolved = await facade.resolve_variant(
            own,
            experiment_key=SURFACE_COHORT_PATH,
            unit_type="cohort",
            unit_id=cohort_id,
            context={"org_id": org_id},
        )
        if not resolved:
            await own.commit()
            return None
        path_id = resolved.config.get("alternative_path_id")
        if not path_id:
            await _expose(own, key=SURFACE_COHORT_PATH, unit_type="cohort",
                          unit_id=cohort_id,
                          context={"surface": "cohort_path", "arm": "control"})
            await own.commit()
            return None
        from app.models.learning_path import LearningPath

        path = await own.get(LearningPath, path_id)
        if path is None or path.org_id != org_id:
            log.warning("experiment_path_override_invalid", path_id=path_id, org_id=org_id)
            await _expose(own, key=SURFACE_COHORT_PATH, unit_type="cohort",
                          unit_id=cohort_id,
                          context={"surface": "cohort_path", "arm": "fallback"})
            await own.commit()
            return None
        await _expose(own, key=SURFACE_COHORT_PATH, unit_type="cohort",
                      unit_id=cohort_id,
                      context={"surface": "cohort_path", "path_id": path_id})
        await own.commit()
        return path_id


@_shield
async def rubric_override(
    db: AsyncSession, *, project_id: str
) -> list | dict | None:
    """Part F: rubric-wording experiment, randomized per project (a rubric is
    shared by every submission of the project — project is the natural
    cluster). The override must be a plausible rubric shape: a non-empty list
    of criterion objects. Unit: project."""
    resolved = await facade.resolve_variant(
        db,
        experiment_key=SURFACE_RUBRIC_WORDING,
        unit_type="project",
        unit_id=project_id,
    )
    if not resolved:
        return None
    rubric = resolved.config.get("rubric")
    if rubric is None:
        await _expose(db, key=SURFACE_RUBRIC_WORDING, unit_type="project",
                      unit_id=project_id, context={"surface": "rubric", "arm": "control"})
        return None
    if not isinstance(rubric, list) or not rubric or not all(
        isinstance(item, dict) and item.get("criterion") for item in rubric
    ):
        log.warning("experiment_rubric_override_invalid", project_id=project_id)
        await _expose(db, key=SURFACE_RUBRIC_WORDING, unit_type="project",
                      unit_id=project_id, context={"surface": "rubric", "arm": "fallback"})
        return None
    await _expose(db, key=SURFACE_RUBRIC_WORDING, unit_type="project",
                  unit_id=project_id, context={"surface": "rubric"})
    return rubric


@_shield
async def retry_policy_override(db: AsyncSession, *, tenant_id: str) -> int | None:
    """Operational: per-tenant step retry budget (clamped 1..10). Unit: tenant."""
    resolved = await facade.resolve_variant(
        db,
        experiment_key=SURFACE_RETRY_POLICY,
        unit_type="tenant",
        unit_id=tenant_id,
    )
    if not resolved:
        return None
    attempts = resolved.config.get("max_attempts")
    if attempts is None:
        await _expose(db, key=SURFACE_RETRY_POLICY, unit_type="tenant",
                      unit_id=tenant_id, context={"surface": "retry_policy", "arm": "control"})
        return None
    if not isinstance(attempts, int):
        await _expose(db, key=SURFACE_RETRY_POLICY, unit_type="tenant",
                      unit_id=tenant_id, context={"surface": "retry_policy", "arm": "fallback"})
        return None
    clamped = max(RETRY_ATTEMPTS_MIN, min(RETRY_ATTEMPTS_MAX, attempts))
    await _expose(db, key=SURFACE_RETRY_POLICY, unit_type="tenant",
                  unit_id=tenant_id, context={"surface": "retry_policy", "max_attempts": clamped})
    return clamped
