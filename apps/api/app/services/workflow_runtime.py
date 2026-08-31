"""Workflow execution runtime (ADR-010 §D6).

Design contract:
- Every state transition is a conditional UPDATE with an expected-status
  guard; 0 rows updated = lost race, the loser backs off silently (R11).
- The run's definition is frozen at creation (definition_snapshot) — running
  workflows never observe definition changes (D1).
- Review gates suspend as durable rows (WorkflowStepReview); a decision is
  persisted state, never an ephemeral event (REV-4).
- provider_action steps execute inside a tracked background task with its own
  DB session: write-ahead provider_request_id + lease committed BEFORE the
  outbound call (R13), output bounded to 48KB.
- Cancellation is a request that terminal-state guards make safe: an in-flight
  provider completion simply loses its conditional UPDATE.

Phase-1 step semantics:
- instruction: completes immediately (human-readable doc step), no outputs
- prompt_template: renders closed moustache refs; first output port = rendered text
- asset_input: each output port takes the run input value with the same key
- transform: whitelisted ops (concat_text/select_field are real; crop/resize
  pass through the asset ref with the operation recorded — no media processing)
- provider_action: adapter call via resolved offering
- review_gate: suspends run; decision approved → passthrough, rejected → step FAILED
- output: passthrough marker
"""

import asyncio
import json
import re
import secrets
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import AppError
from app.models.organization import Organization
from app.models.provider import (
    OrgCredential,
    ProviderAdapter,
    ProviderConnection,
    ProviderModelOffering,
)
from app.models.workflow_pack import WorkflowPackInstallation
from app.models.workflow_run import (
    RunStatus,
    StepRunStatus,
    WorkflowRun,
    WorkflowRunEvent,
    WorkflowStepBinding,
    WorkflowStepReview,
    WorkflowStepRun,
)

log = structlog.get_logger()

MAX_STEP_OUTPUT_BYTES = 48 * 1024  # Airflow XCom lesson
# NUL + C0/C1 controls (tab/newline allowed) — crash asyncpg on JSONB write
_CTRL_CHAR_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def _values_have_ctrl(v) -> bool:
    """True if any string ANYWHERE in a nested structure holds a control char,
    OR any float is non-finite (NaN/Infinity/-Infinity).
    Must walk real values — json.dumps escapes NUL so a serialized scan would
    miss it. Tuples are included: json.dumps serializes them as arrays, so a
    tuple-bearing adapter output would otherwise slip past.

    Non-finite floats (R73): stdlib json.loads accepts bare NaN/Infinity tokens
    (so run inputs carry real float('nan')), and adapter outputs may compute
    one; SQLAlchemy's default JSONB serializer (allow_nan=True) re-emits the
    literal `NaN`/`Infinity` token, which Postgres rejects with 22P02
    (InvalidTextRepresentation → DBAPIError → 500). Screening here covers BOTH
    the create_run input path and the adapter-output settlement path (bool is
    an int subclass, not float, so booleans are unaffected).

    ITERATIVE — json.loads parses ~990 levels deep (a 2KB payload passing
    every size cap), where a recursive scan RecursionErrors into the very
    500 this guard exists to prevent (round-18 fixed the comfyui/matching
    siblings; this one had the same defect)."""
    import math

    stack = [v]
    while stack:
        cur = stack.pop()
        if isinstance(cur, str):
            if _CTRL_CHAR_RE.search(cur):
                return True
        elif isinstance(cur, float):
            if not math.isfinite(cur):
                return True
        elif isinstance(cur, dict):
            stack.extend(cur.keys())
            stack.extend(cur.values())
        elif isinstance(cur, (list, tuple)):
            stack.extend(cur)
    return False


# Max JSON nesting depth for a run input. A json-typed value can be a
# dict/list under the 8,000-char size gate yet nested hundreds of levels
# deep (`[[[...]]]` is ~2 chars/level); pydantic's response serializer
# (which echoes inputs on the run response) blows its own recursion guard
# around depth ~400 → a 500 the size/type checks never catch. Bound it here
# as a clean 422, well below any serializer/parser limit (round-35).
_MAX_INPUT_DEPTH = 64


def _max_depth(v) -> int:
    """Deepest nesting level of a JSON value (iterative — never recurses)."""
    deepest = 0
    stack = [(v, 1)]
    while stack:
        cur, d = stack.pop()
        if d > deepest:
            deepest = d
        if isinstance(cur, dict):
            for val in cur.values():
                stack.append((val, d + 1))
        elif isinstance(cur, (list, tuple)):
            for x in cur:
                stack.append((x, d + 1))
    return deepest


def _iter_strings(v):
    """Yield every raw string value in a nested structure (keys excluded).
    Used by expression scanners that must see exactly what the renderer
    sees — never a json.dumps serialization, whose escapes defeat \\s*.
    Iterative — recursive generators blow the stack well before json.loads
    stops accepting deeper input."""
    stack = [v]
    while stack:
        cur = stack.pop()
        if isinstance(cur, str):
            yield cur
        elif isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, (list, tuple)):
            stack.extend(cur)


_EXPR_RE = re.compile(r"\{\{\s*([a-z0-9_.]+)\s*\}\}")
_STEP_REF_RE = re.compile(r"^steps\.([a-z0-9_]+)\.outputs\.[a-z0-9_]+$")


def _template_ref_upstreams(step: dict) -> set[str]:
    """Step ids referenced via moustache in a prompt_template's config.

    Template refs are DATA dependencies: rendering an unready ref yields ''
    and silently corrupts output, so the scheduler must order on them exactly
    like edges. Scoped to prompt_template — the only step type whose config
    is rendered at execution time.
    """
    if step.get("type") != "prompt_template":
        return set()
    refs: set[str] = set()
    # Scan the RAW string values, not json.dumps — dumps escapes a newline
    # inside {{ }} to the 2-char \n sequence, which \s* never matches, while
    # the renderer operates on the raw template where \s* DOES match it. The
    # scanner must see exactly what the renderer sees.
    for text in _iter_strings(step.get("config", {})):
        for m in _EXPR_RE.finditer(text):
            rm = _STEP_REF_RE.match(m.group(1))
            if rm:
                refs.add(rm.group(1))
    return refs


def _upstream_ids(step_id: str, steps: dict, edges: list) -> set[str]:
    """Combined upstreams: edge upstreams + template-ref data dependencies."""
    ups = {e["from_step"] for e in edges if e["to_step"] == step_id}
    step = steps.get(step_id)
    if step is not None:
        ups |= _template_ref_upstreams(step)
    return ups


# Tracked background tasks (webhook.py pattern) — drained on shutdown
_pending_tasks: set[asyncio.Task] = set()


def _track(coro) -> asyncio.Task:
    task = asyncio.create_task(coro)
    _pending_tasks.add(task)
    task.add_done_callback(_pending_tasks.discard)
    return task


async def drain_workflow_tasks(timeout: float = 15.0) -> None:
    """Await in-flight workflow executions (lifespan shutdown / tests).

    Only drains tasks bound to the CURRENT event loop — tasks left over from
    a previous, closed loop (test isolation) can never complete and would
    make gather() raise; they are discarded from the tracking set instead.
    """
    if not _pending_tasks:
        return
    loop = asyncio.get_running_loop()
    current = [t for t in _pending_tasks if t.get_loop() is loop]
    stale = [t for t in _pending_tasks if t.get_loop() is not loop]
    for t in stale:
        _pending_tasks.discard(t)
    if not current:
        return
    try:
        await asyncio.wait_for(asyncio.gather(*current, return_exceptions=True), timeout=timeout)
    except TimeoutError:
        log.warning("workflow_drain_timeout", pending=len(current))
    # CancelledError propagates: a lifespan-shutdown cancellation must not be
    # swallowed (or mislabelled as a timeout) — gather(return_exceptions=True)
    # already absorbs task-level exceptions, so nothing else can raise here.


def _now() -> datetime:
    return datetime.now(UTC)


class WorkflowRuntimeService:
    """Request-session operations: create, read, decide, cancel."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Run creation ──────────────────────────────────────

    async def create_run(
        self,
        org_id: str,
        installation_id: str,
        inputs: dict,
        started_by: str,
        idempotency_key: str | None = None,
    ) -> WorkflowRun:
        from app.models.skill_pack import InstallStatus

        install = await self.db.get(WorkflowPackInstallation, installation_id)
        if install is None or install.org_id != org_id or install.status == InstallStatus.REMOVED:
            raise AppError("INSTALLATION_NOT_FOUND", "Workflow installation not found", 404)

        # Issue #27 §2.5: suspended tenants cannot start costed executions;
        # active tenants are bounded by max_workflow_runs_month.
        from app.controlplane import facade as cp_facade

        tenant = await cp_facade.get_tenant_for_org(self.db, org_id)
        cp_facade.require_tenant_active(tenant)
        month_start = _now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        from app.models.organization import Organization as _Org

        run_count = (
            await self.db.execute(
                select(func.count(WorkflowRun.id))
                .join(_Org, _Org.id == WorkflowRun.org_id)
                .where(
                    _Org.tenant_id == tenant.id,
                    WorkflowRun.created_at >= month_start,
                )
            )
        ).scalar_one()
        await cp_facade.check_quota(self.db, tenant, "max_workflow_runs_month", current=run_count)

        # Resolve the effective definition: forked local copy or release manifest
        definition = install.local_definition
        if definition is None:
            if install.release_id is None:
                raise AppError(
                    "NO_DEFINITION", "Installation has no release or local definition", 422
                )
            from app.models.workflow_pack import WorkflowPackRelease

            release = await self.db.get(WorkflowPackRelease, install.release_id)
            if release is None:
                raise AppError("NO_DEFINITION", "Release no longer exists", 422)
            definition = release.manifest.get("definition", {})

        # Validate run inputs against the definition's input schema
        input_defs = {i["key"]: i for i in definition.get("inputs", [])}
        for key, idef in input_defs.items():
            if idef.get("required", True) and key not in inputs and idef.get("default") is None:
                raise AppError("MISSING_INPUT", f"Required input '{key}' not provided", 422)
        unknown = set(inputs.keys()) - set(input_defs.keys())
        if unknown:
            raise AppError("UNKNOWN_INPUT", f"Unknown inputs: {', '.join(sorted(unknown))}", 422)
        # Apply defaults. Defaults are stored as strings (schema), so a
        # json-typed default must be parsed here or the type check below
        # would reject the pack's own published default (422, never a 500).
        effective_inputs = dict(inputs)
        for key, idef in input_defs.items():
            if key not in effective_inputs and idef.get("default") is not None:
                default = idef["default"]
                if idef.get("type") == "json" and isinstance(default, str):
                    try:
                        default = json.loads(default)
                    except (ValueError, TypeError):
                        raise AppError(
                            "INVALID_INPUT_VALUE",
                            f"Default for input '{key}' is not valid JSON",
                            422,
                        ) from None
                effective_inputs[key] = default
        # Per-type value validation — selection options enforced, text bounded,
        # asset refs must be short strings (never blobs), json shape-checked.
        for key, value in effective_inputs.items():
            idef = input_defs.get(key)
            if idef is None:
                continue
            itype = idef.get("type", "text")
            if itype == "selection":
                options = idef.get("options") or []
                if value not in options:
                    raise AppError(
                        "INVALID_INPUT_VALUE",
                        f"Input '{key}' must be one of: {', '.join(str(o) for o in options)}",
                        422,
                    )
            elif itype in ("text", "prompt"):
                if not isinstance(value, str) or len(value) > 8000:
                    raise AppError(
                        "INVALID_INPUT_VALUE",
                        f"Input '{key}' must be a string of at most 8,000 characters",
                        422,
                    )
            elif itype in ("image", "video", "audio", "reference_asset"):
                if not isinstance(value, str) or len(value) > 500:
                    raise AppError(
                        "INVALID_INPUT_VALUE",
                        f"Input '{key}' must be an asset reference string (max 500 chars)",
                        422,
                    )
            elif itype == "json":
                if not isinstance(value, (dict, list)) or len(str(value)) > 8000:
                    raise AppError(
                        "INVALID_INPUT_VALUE",
                        f"Input '{key}' must be a JSON object or array (max 8,000 chars)",
                        422,
                    )
                # A small-but-deeply-nested json value passes the size gate
                # but overflows the response serializer's recursion guard
                # (~400) → 500 on run creation. Reject as a clean 422.
                if _max_depth(value) > _MAX_INPUT_DEPTH:
                    raise AppError(
                        "INVALID_INPUT_VALUE",
                        f"Input '{key}' is nested too deeply (max {_MAX_INPUT_DEPTH} levels)",
                        422,
                    )
        # Bound input payload + reject NUL/control chars (stored into JSONB;
        # asyncpg raises UntranslatableCharacterError → 500 otherwise). Scan
        # the ACTUAL string values, not json.dumps — dumps escapes NUL to the
        # 6-char \\u0000 sequence, which the control-char regex never matches.
        if len(json.dumps(effective_inputs, ensure_ascii=False)) > MAX_STEP_OUTPUT_BYTES:
            raise AppError("WF_INPUT_TOO_LARGE", "Run inputs exceed 48KB", 422)
        if _values_have_ctrl(effective_inputs):
            raise AppError(
                "INVALID_INPUT_VALUE",
                "Inputs contain NUL/control characters or NaN/Infinity values that are not allowed",
                422,
            )

        # Concurrency cap (config: workflow_max_concurrent_runs). Every
        # active run can be mid-provider-call spending real money — without
        # a cap, any org member can fan out unbounded concurrent runs (the
        # per-user rate limit only bounds creations per minute, and multiple
        # members compound). Checked BEFORE the idempotency lookup would be
        # wrong: an idempotent retry of an existing run must still succeed
        # at the cap, so the gate sits after it. Soft limit (no FOR UPDATE):
        # a burst racing the count may overshoot by a few — acceptable for a
        # spend guard, same trade-off as MAX_CONNECTIONS_PER_ORG.
        active_statuses = (RunStatus.PENDING, RunStatus.RUNNING, RunStatus.WAITING_REVIEW)

        # Idempotent creation
        if idempotency_key:
            existing_r = await self.db.execute(
                select(WorkflowRun).where(
                    WorkflowRun.org_id == org_id,
                    WorkflowRun.idempotency_key == idempotency_key,
                )
            )
            existing = existing_r.scalar_one_or_none()
            if existing is not None:
                # The uniqueness index is (org_id, key): a DIFFERENT member
                # reusing the same key must NOT receive this run — that would
                # hand them its id/inputs/outputs, bypassing the run-read
                # scoping (R58). A cross-member key collision is a conflict,
                # not a retry.
                if existing.started_by != started_by:
                    raise AppError(
                        "IDEMPOTENCY_KEY_CONFLICT",
                        "This idempotency key is already in use in this organization",
                        409,
                    )
                # Idempotency must be scoped to the SAME request — reusing a
                # key with a different installation or inputs is a client bug,
                # not a retry; returning the old run would silently ignore the
                # new intent.
                if (
                    existing.installation_id != installation_id
                    or existing.inputs != effective_inputs
                ):
                    raise AppError(
                        "IDEMPOTENCY_KEY_CONFLICT",
                        "This idempotency key was already used with different inputs",
                        409,
                    )
                return existing

        active_r = await self.db.execute(
            select(func.count()).where(
                WorkflowRun.org_id == org_id,
                WorkflowRun.status.in_(active_statuses),
            )
        )
        if active_r.scalar_one() >= settings.workflow_max_concurrent_runs:
            raise AppError(
                "WF_TOO_MANY_ACTIVE_RUNS",
                (
                    f"Organization already has {settings.workflow_max_concurrent_runs} "
                    "active workflow runs — wait for one to finish or cancel it"
                ),
                422,
            )

        run = WorkflowRun(
            org_id=org_id,
            pack_id=install.pack_id,
            release_id=install.release_id,
            installation_id=installation_id,
            definition_snapshot=definition,
            inputs=effective_inputs,
            started_by=started_by,
            idempotency_key=idempotency_key,
        )
        try:
            async with self.db.begin_nested():
                self.db.add(run)
                await self.db.flush()
        except IntegrityError:
            # Concurrent idempotent create — return the winner. Only assume
            # the idempotency index when a key was actually supplied; any
            # other constraint violation must not be masked as NoResultFound.
            if idempotency_key is not None:
                existing_r = await self.db.execute(
                    select(WorkflowRun).where(
                        WorkflowRun.org_id == org_id,
                        WorkflowRun.idempotency_key == idempotency_key,
                    )
                )
                existing = existing_r.scalar_one_or_none()
                if existing is not None:
                    # Same cross-member guard as the pre-check path: a
                    # concurrent create under this key by a DIFFERENT member
                    # must not have its run handed back to this caller.
                    if existing.started_by != started_by:
                        raise AppError(
                            "IDEMPOTENCY_KEY_CONFLICT",
                            "This idempotency key is already in use in this organization",
                            409,
                        ) from None
                    return existing
            raise

        # Pre-create all step runs as PENDING
        for step in definition.get("steps", []):
            self.db.add(
                WorkflowStepRun(
                    run_id=run.id,
                    step_id=step["id"],
                    step_type=step["type"],
                    max_attempts=3,
                )
            )
        self.db.add(WorkflowRunEvent(run_id=run.id, event_type="run_created", payload={}))
        await self.db.flush()
        log.info("workflow_run_created", run_id=run.id, org_id=org_id)
        return run

    # ── Reads ─────────────────────────────────────────────

    async def get_run(
        self, run_id: str, org_id: str, only_user_id: str | None = None
    ) -> WorkflowRun:
        run = await self.db.get(WorkflowRun, run_id)
        if run is None or run.org_id != org_id:
            raise AppError("RUN_NOT_FOUND", "Workflow run not found", 404)
        # only_user_id (non-instructors): a peer's run detail exposes their
        # inputs/outputs — uniform 404 so run ids stay non-enumerable. The
        # cancel/advance internals pass only_user_id=None (they enforce their
        # own rules and must see any run).
        if only_user_id is not None and run.started_by != only_user_id:
            raise AppError("RUN_NOT_FOUND", "Workflow run not found", 404)
        return run

    async def list_runs(
        self,
        org_id: str,
        page: int = 1,
        per_page: int = 20,
        only_user_id: str | None = None,
    ) -> tuple[list[WorkflowRun], int]:
        from sqlalchemy import func

        # only_user_id scopes to the caller's own runs (non-instructors) —
        # run inputs/outputs carry the initiator's prompts and private asset
        # references, so peers must not enumerate each other's work
        # (mirrors project submission-list scoping).
        base = select(WorkflowRun).where(WorkflowRun.org_id == org_id)
        if only_user_id is not None:
            base = base.where(WorkflowRun.started_by == only_user_id)
        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        result = await self.db.execute(
            base.order_by(WorkflowRun.created_at.desc(), WorkflowRun.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_step_runs(self, run_id: str) -> list[WorkflowStepRun]:
        result = await self.db.execute(
            select(WorkflowStepRun)
            .where(WorkflowStepRun.run_id == run_id)
            .order_by(WorkflowStepRun.created_at)
        )
        return list(result.scalars().all())

    async def get_events(self, run_id: str) -> list[WorkflowRunEvent]:
        result = await self.db.execute(
            select(WorkflowRunEvent)
            .where(WorkflowRunEvent.run_id == run_id)
            .order_by(WorkflowRunEvent.created_at)
        )
        return list(result.scalars().all())

    async def get_open_reviews(self, org_id: str) -> list[WorkflowStepReview]:
        result = await self.db.execute(
            select(WorkflowStepReview)
            .where(WorkflowStepReview.org_id == org_id, WorkflowStepReview.decision.is_(None))
            .order_by(WorkflowStepReview.due_at)
        )
        return list(result.scalars().all())

    # ── Review decision (Temporal Update semantics: validate-then-accept) ──

    async def decide_review(
        self, review_id: str, org_id: str, decision: str, note: str | None, decided_by: str
    ) -> WorkflowStepReview:
        if decision not in ("approved", "rejected"):
            raise AppError("INVALID_DECISION", "Decision must be approved or rejected", 422)

        # Lock order MUST be steps → reviews → run to match cancel_run and the
        # executor — otherwise decide_review (review-first) vs cancel_run
        # (step-first) deadlock under concurrency (observed live). Resolve the
        # step id without a lock, take the step lock first, THEN the review
        # lock (concurrent decisions still serialize on the review row).
        pre = await self.db.execute(
            select(WorkflowStepReview.step_run_id).where(WorkflowStepReview.id == review_id)
        )
        step_run_id = pre.scalar_one_or_none()
        if step_run_id is None:
            raise AppError("REVIEW_NOT_FOUND", "Review not found", 404)
        await self.db.execute(
            select(WorkflowStepRun.id).where(WorkflowStepRun.id == step_run_id).with_for_update()
        )
        result = await self.db.execute(
            select(WorkflowStepReview).where(WorkflowStepReview.id == review_id).with_for_update()
        )
        review = result.scalar_one_or_none()
        if review is None or review.org_id != org_id:
            raise AppError("REVIEW_NOT_FOUND", "Review not found", 404)
        if review.decision is not None:
            raise AppError("WF_REVIEW_ALREADY_DECIDED", "This review was already decided", 409)

        review.decision = decision
        review.decision_note = note
        review.decided_by = decided_by
        review.decided_at = _now()

        step_run = await self.db.get(WorkflowStepRun, review.step_run_id)
        if step_run is None:
            raise AppError("RUN_NOT_FOUND", "Step run not found", 404)

        run = await self.db.get(WorkflowRun, step_run.run_id)
        if run is None:
            raise AppError("RUN_NOT_FOUND", "Run not found", 404)

        step_def = self._step_def(run.definition_snapshot, step_run.step_id)
        if decision == "approved":
            # Passthrough output: decision port + first-input passthrough.
            # "First" = the step's first DECLARED input port with a resolved
            # value. inputs_resolved here is read back from the persisted
            # JSONB column, and Postgres jsonb re-sorts object keys by length
            # then bytewise — bare next(iter(...)) would pass through the
            # input with the SHORTEST PORT NAME, not the author's primary
            # input (same class as the R43 transform ordering fix).
            output: dict = {"decision": "approved"}
            inputs_resolved = step_run.inputs_resolved or {}
            declared_ports = [p["port"] for p in (step_def or {}).get("inputs", [])]
            first_val = next(
                (inputs_resolved[p] for p in declared_ports if p in inputs_resolved),
                next(iter(inputs_resolved.values()), None),
            )
            for port in (step_def or {}).get("outputs", []):
                if port["port"] != "decision" and first_val is not None:
                    output[port["port"]] = first_val
            # This passthrough write bypasses _complete_step, so it must
            # enforce the same MAX_STEP_OUTPUT_BYTES bound every executor
            # settlement does — a review gate fanning a large upstream output
            # into multiple 'passed' ports could otherwise persist an oversized
            # JSONB row that no other step path would accept. Fail the step
            # (WF_OUTPUT_TOO_LARGE → run FAILED via SKIPPED propagation)
            # rather than write an over-limit row.
            if len(json.dumps(output, ensure_ascii=False, default=str)) > MAX_STEP_OUTPUT_BYTES:
                await self.db.execute(
                    update(WorkflowStepRun)
                    .where(
                        WorkflowStepRun.id == step_run.id,
                        WorkflowStepRun.status == StepRunStatus.WAITING_REVIEW,
                    )
                    .values(
                        status=StepRunStatus.FAILED,
                        error_code="WF_OUTPUT_TOO_LARGE",
                        error="Review passthrough output exceeds 48KB",
                        finished_at=_now(),
                    )
                )
                self.db.add(
                    WorkflowRunEvent(
                        run_id=run.id,
                        step_id=step_run.step_id,
                        event_type="step_failed",
                        payload={"error_code": "WF_OUTPUT_TOO_LARGE"},
                    )
                )
                await self.db.execute(
                    update(WorkflowRun)
                    .where(WorkflowRun.id == run.id, WorkflowRun.status == RunStatus.WAITING_REVIEW)
                    .values(status=RunStatus.RUNNING)
                )
                await self.db.flush()
                return review
            await self.db.execute(
                update(WorkflowStepRun)
                .where(
                    WorkflowStepRun.id == step_run.id,
                    WorkflowStepRun.status == StepRunStatus.WAITING_REVIEW,
                )
                .values(status=StepRunStatus.COMPLETED, output=output, finished_at=_now())
            )
            self.db.add(
                WorkflowRunEvent(
                    run_id=run.id,
                    step_id=step_run.step_id,
                    event_type="review_decided",
                    payload={"decision": "approved"},
                )
            )
            # Run resumes
            await self.db.execute(
                update(WorkflowRun)
                .where(WorkflowRun.id == run.id, WorkflowRun.status == RunStatus.WAITING_REVIEW)
                .values(status=RunStatus.RUNNING)
            )
        else:
            await self.db.execute(
                update(WorkflowStepRun)
                .where(
                    WorkflowStepRun.id == step_run.id,
                    WorkflowStepRun.status == StepRunStatus.WAITING_REVIEW,
                )
                .values(
                    status=StepRunStatus.FAILED,
                    error_code="WF_REVIEW_REJECTED",
                    error=note or "Review rejected",
                    finished_at=_now(),
                )
            )
            self.db.add(
                WorkflowRunEvent(
                    run_id=run.id,
                    step_id=step_run.step_id,
                    event_type="review_decided",
                    payload={"decision": "rejected"},
                )
            )
            # Resume the run so the advance loop can propagate SKIPPED and
            # settle the run into FAILED
            await self.db.execute(
                update(WorkflowRun)
                .where(WorkflowRun.id == run.id, WorkflowRun.status == RunStatus.WAITING_REVIEW)
                .values(status=RunStatus.RUNNING)
            )
        await self.db.flush()
        return review

    # ── Cancellation ──────────────────────────────────────

    async def cancel_run(
        self, run_id: str, org_id: str, acting_user_id: str, is_instructor: bool = False
    ) -> WorkflowRun:
        # R90e: scope the lookup for non-instructors to their own runs, so a
        # peer's (or instructor's) run id resolves to 404 here just as it does
        # in get_run. Otherwise cancel_run was an existence oracle — 403
        # RUN_CANCEL_FORBIDDEN for an existing peer run vs 404 for a nonexistent
        # id — defeating get_run's uniform-404 non-enumerability. Instructors
        # keep org-wide reach (only_user_id=None).
        run = await self.get_run(
            run_id, org_id, only_user_id=None if is_instructor else acting_user_id
        )
        # Belt-and-suspenders: the run's initiator or an instructor+ may cancel.
        # (For a non-instructor the get_run scope already guarantees ownership;
        # this also covers the started_by-is-NULL orphan case → instructor-only.)
        if not is_instructor and run.started_by != acting_user_id:
            raise AppError(
                "RUN_CANCEL_FORBIDDEN",
                "Only the run initiator or an instructor can cancel this run",
                403,
            )
        if run.status in (RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED):
            raise AppError("RUN_ALREADY_FINISHED", "Run is already in a terminal state", 409)

        # Lock ORDER matters: the executor claims step rows first and touches
        # the run row last — cancel must use the same order (steps → reviews
        # → run) or the two transactions deadlock under contention.

        # 1. Cancel all non-terminal steps (in-flight provider completions
        #    will lose their conditional UPDATE — safe)
        await self.db.execute(
            update(WorkflowStepRun)
            .where(
                WorkflowStepRun.run_id == run_id,
                WorkflowStepRun.status.in_(
                    [
                        StepRunStatus.PENDING,
                        StepRunStatus.READY,
                        StepRunStatus.RUNNING,
                        StepRunStatus.WAITING_REVIEW,
                        StepRunStatus.WAITING_RETRY,
                    ]
                ),
            )
            .values(status=StepRunStatus.CANCELLED, finished_at=_now())
        )
        # 2. Expire open reviews for this run's steps
        step_ids_r = await self.db.execute(
            select(WorkflowStepRun.id).where(WorkflowStepRun.run_id == run_id)
        )
        step_ids = [row[0] for row in step_ids_r.all()]
        if step_ids:
            await self.db.execute(
                update(WorkflowStepReview)
                .where(
                    WorkflowStepReview.step_run_id.in_(step_ids),
                    WorkflowStepReview.decision.is_(None),
                )
                .values(decision="expired", decided_at=_now())
            )
        # 3. Run row LAST (matches executor lock order)
        result = await self.db.execute(
            update(WorkflowRun)
            .where(
                WorkflowRun.id == run_id,
                WorkflowRun.status.in_(
                    [RunStatus.PENDING, RunStatus.RUNNING, RunStatus.WAITING_REVIEW]
                ),
            )
            .values(status=RunStatus.CANCELLED, error_code="WF_CANCELLED", finished_at=_now())
        )
        # Only record the event when THIS request actually flipped the run —
        # a lost race (concurrent completion) must not fabricate a
        # run_cancelled event for a run that was never cancelled.
        if result.rowcount:
            self.db.add(WorkflowRunEvent(run_id=run_id, event_type="run_cancelled", payload={}))
        await self.db.flush()
        await self.db.refresh(run)
        return run

    @staticmethod
    def _step_def(definition: dict, step_id: str) -> dict | None:
        for step in definition.get("steps", []):
            if step["id"] == step_id:
                return step
        return None


# ══════════════════════════════════════════════════════════
# Executor engine — runs with its OWN sessions (dispatched after commit)
# ══════════════════════════════════════════════════════════


def dispatch_advance(run_id: str) -> None:
    """Schedule the advance loop as a tracked background task.

    Call AFTER the request transaction commits so the executor's separate
    session can see the run rows.
    """
    _track(advance_run(run_id))


async def advance_run(run_id: str) -> None:
    """Advance a run: execute all ready steps until blocked or terminal."""
    from app.core.database import AsyncSessionLocal

    try:
        for _ in range(200):  # hard bound: no infinite loops (≤50 steps × retries)
            async with AsyncSessionLocal() as db:
                progressed = await _advance_once(db, run_id)
                await db.commit()
            if not progressed:
                break
    except Exception:
        log.exception("workflow_advance_crashed", run_id=run_id)


async def _advance_once(db: AsyncSession, run_id: str) -> bool:
    """One advance iteration. Returns True if any progress was made."""
    run = await db.get(WorkflowRun, run_id)
    if run is None:
        return False

    # PENDING → RUNNING (conditional)
    if run.status == RunStatus.PENDING:
        result = await db.execute(
            update(WorkflowRun)
            .where(WorkflowRun.id == run_id, WorkflowRun.status == RunStatus.PENDING)
            .values(status=RunStatus.RUNNING, started_at=_now())
        )
        if result.rowcount:
            db.add(WorkflowRunEvent(run_id=run_id, event_type="run_started", payload={}))
        await db.refresh(run)

    if run.status not in (RunStatus.RUNNING,):
        return False

    definition = run.definition_snapshot
    steps = {s["id"]: s for s in definition.get("steps", [])}
    edges = definition.get("edges", [])

    step_runs_r = await db.execute(select(WorkflowStepRun).where(WorkflowStepRun.run_id == run_id))
    step_runs = {sr.step_id: sr for sr in step_runs_r.scalars().all()}

    # Propagate SKIPPED: any step downstream of a FAILED/SKIPPED/CANCELLED
    # step — via edges OR template-ref data dependencies. Fixpoint loop:
    # a single pass in dict order only advances one hop over reverse-
    # topologically ordered rows; multi-hop chains must fully settle in ONE
    # _advance_once call so the terminal check below sees final statuses.
    changed_any = False
    local_status = {step_id: sr.status for step_id, sr in step_runs.items()}
    while True:
        changed = False
        for step_id, sr in step_runs.items():
            if local_status[step_id] != StepRunStatus.PENDING:
                continue
            upstream = _upstream_ids(step_id, steps, edges)
            if any(
                local_status[u]
                in (StepRunStatus.FAILED, StepRunStatus.SKIPPED, StepRunStatus.CANCELLED)
                for u in upstream
                if u in local_status
            ):
                result = await db.execute(
                    update(WorkflowStepRun)
                    .where(
                        WorkflowStepRun.id == sr.id, WorkflowStepRun.status == StepRunStatus.PENDING
                    )
                    .values(status=StepRunStatus.SKIPPED, finished_at=_now())
                )
                if result.rowcount:
                    local_status[step_id] = StepRunStatus.SKIPPED
                    changed = True
        changed_any = changed_any or changed
        if not changed:
            break

    # Refresh statuses after skip propagation
    if changed_any:
        step_runs_r = await db.execute(
            select(WorkflowStepRun).where(WorkflowStepRun.run_id == run_id)
        )
        step_runs = {sr.step_id: sr for sr in step_runs_r.scalars().all()}

    # Find one executable step (upstreams all COMPLETED — edges + template refs)
    for step_id, sr in step_runs.items():
        if sr.status not in (StepRunStatus.PENDING, StepRunStatus.WAITING_RETRY):
            continue
        upstream = _upstream_ids(step_id, steps, edges)
        if all(step_runs[u].status == StepRunStatus.COMPLETED for u in upstream if u in step_runs):
            executed = await _execute_step(db, run, steps[step_id], sr, edges, step_runs)
            if executed:
                return True  # made progress; loop again

    # No executable step: check for run completion
    terminal = {
        StepRunStatus.COMPLETED,
        StepRunStatus.FAILED,
        StepRunStatus.SKIPPED,
        StepRunStatus.CANCELLED,
    }
    if all(sr.status in terminal for sr in step_runs.values()):
        any_failed = any(sr.status == StepRunStatus.FAILED for sr in step_runs.values())
        if any_failed:
            result = await db.execute(
                update(WorkflowRun)
                .where(WorkflowRun.id == run_id, WorkflowRun.status == RunStatus.RUNNING)
                .values(
                    status=RunStatus.FAILED,
                    error_code="WF_STEP_FAILED",
                    finished_at=_now(),
                )
            )
            if result.rowcount:
                db.add(WorkflowRunEvent(run_id=run_id, event_type="run_failed", payload={}))
                await _emit_run_terminal(db, run, "failed")
        else:
            # Collect workflow outputs ({} is a valid output — only skip None)
            outputs = {}
            for out in definition.get("outputs", []):
                src = step_runs.get(out["from_step"])
                if src is not None and src.output is not None:
                    outputs[out["key"]] = src.output.get(out["from_port"])
            result = await db.execute(
                update(WorkflowRun)
                .where(WorkflowRun.id == run_id, WorkflowRun.status == RunStatus.RUNNING)
                .values(status=RunStatus.COMPLETED, outputs=outputs, finished_at=_now())
            )
            if result.rowcount:
                db.add(WorkflowRunEvent(run_id=run_id, event_type="run_completed", payload={}))
                await _emit_run_terminal(db, run, "completed")
    return False


async def _emit_run_terminal(db: AsyncSession, run: WorkflowRun, status: str) -> None:
    """Issue #27 §3.3b: one workflow_run usage event per run — BOTH outcomes,
    metadata carries status (pricing may exclude failed via policy params).
    Guarded by the terminal-transition rowcount + the idempotency key. Also
    posts the run.terminal outbox message (reservation settlement, P5)."""
    from app.controlplane import facade as cp_facade
    from app.controlplane.models.outbox import enqueue

    tenant_id = (
        await db.execute(select(Organization.tenant_id).where(Organization.id == run.org_id))
    ).scalar_one_or_none()
    if tenant_id is None:
        return
    await cp_facade.emit_usage(
        db,
        tenant_id=tenant_id,
        org_id=run.org_id,
        usage_type="workflow_run",
        quantity=1,
        occurred_at=_now(),
        source="workflow_runtime",
        idempotency_key=f"wfrun:{run.id}",
        workflow_run_id=run.id,
        user_id=run.started_by,
        metadata={"status": status},
    )
    enqueue(db, "run.terminal", {"run_id": run.id, "status": status})


def _resolve_step_inputs(step: dict, run: WorkflowRun, edges: list, step_runs: dict) -> dict:
    """Resolve a step's input port values from upstream outputs / run inputs."""
    resolved: dict = {}
    for edge in edges:
        if edge["to_step"] != step["id"]:
            continue
        src = step_runs.get(edge["from_step"])
        if src is not None and src.output is not None:
            resolved[edge["to_port"]] = src.output.get(edge["from_port"])
    # asset_input: output ports feed from run inputs by port name
    if step["type"] == "asset_input":
        for port in step.get("outputs", []):
            resolved[port["port"]] = run.inputs.get(port["port"])
    return resolved


def _render_value(v) -> str:
    """Render a resolved ref value as template text.

    str(v) would emit Python repr for dicts/lists (single quotes, True/None)
    — invalid JSON when the template builds a JSON payload. Render
    dict/list as real JSON, None as '' (not 'None'), bool as JSON
    'true'/'false'.
    """
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _render_template(template: str, run: WorkflowRun, step_runs: dict) -> str:
    """Render closed moustache references. Unknown refs render empty (validated at publish)."""

    def _sub(m: re.Match) -> str:
        ref = m.group(1)
        if ref.startswith("inputs."):
            return _render_value(run.inputs.get(ref[len("inputs.") :]))
        if ref.startswith("steps."):
            parts = ref.split(".")
            if len(parts) == 4 and parts[2] == "outputs":
                sr = step_runs.get(parts[1])
                if sr and sr.output:
                    return _render_value(sr.output.get(parts[3]))
        return ""

    return _EXPR_RE.sub(_sub, template)


async def _execute_step(
    db: AsyncSession,
    run: WorkflowRun,
    step: dict,
    sr: WorkflowStepRun,
    edges: list,
    step_runs: dict,
) -> bool:
    """Execute one step. Returns True if a transition happened."""
    step_type = step["type"]
    inputs_resolved = _resolve_step_inputs(step, run, edges, step_runs)

    # Fencing token: the attempt number this claim will own. A resurrected
    # executor from an earlier attempt must never settle a newer attempt's
    # row, so every settlement UPDATE also guards on attempt == claimed.
    claimed_attempt = sr.attempt + 1

    # Claim: PENDING/WAITING_RETRY → RUNNING (conditional — R11)
    claim = await db.execute(
        update(WorkflowStepRun)
        .where(
            WorkflowStepRun.id == sr.id,
            WorkflowStepRun.status.in_([StepRunStatus.PENDING, StepRunStatus.WAITING_RETRY]),
            WorkflowStepRun.attempt == sr.attempt,  # fence the claim itself too
        )
        .values(
            status=StepRunStatus.RUNNING,
            inputs_resolved=inputs_resolved,
            started_at=_now(),
            attempt=WorkflowStepRun.attempt + 1,
            lease_expires_at=_now()
            + timedelta(seconds=settings.workflow_step_timeout_seconds + 30),
        )
    )
    if not claim.rowcount:
        return False  # lost the race
    db.add(
        WorkflowRunEvent(run_id=run.id, step_id=step["id"], event_type="step_started", payload={})
    )
    await db.flush()

    try:
        if step_type == "instruction" or step_type == "output":
            if step_type == "output":
                # Key by DECLARED OUTPUT port names — downstream edges and
                # workflow-output collection read by output port, and the
                # duplicate-port rule makes input/output names disjoint, so
                # keeping input-port keys would make every value unreachable.
                in_ports = [p["port"] for p in step.get("inputs", [])]
                out_ports = [p["port"] for p in step.get("outputs", [])]
                output = {}
                for i, out_port in enumerate(out_ports):
                    if len(in_ports) == 1:
                        # Single input fans out to every declared output port
                        output[out_port] = inputs_resolved.get(in_ports[0])
                    elif i < len(in_ports):
                        output[out_port] = inputs_resolved.get(in_ports[i])
                    else:
                        output[out_port] = None  # port beyond the input count
            else:
                output = {}
            await _complete_step(db, run, sr, output, claimed_attempt)
        elif step_type == "prompt_template":
            rendered = _render_template(step.get("config", {}).get("template", ""), run, step_runs)
            ports = step.get("outputs", [])
            output = {ports[0]["port"]: rendered} if ports else {}
            await _complete_step(db, run, sr, output, claimed_attempt)
        elif step_type == "asset_input":
            await _complete_step(db, run, sr, inputs_resolved, claimed_attempt)
        elif step_type == "transform":
            output = _run_transform(step.get("config", {}), inputs_resolved, step)
            await _complete_step(db, run, sr, output, claimed_attempt)
        elif step_type == "review_gate":
            await _suspend_for_review(db, run, sr, step, claimed_attempt)
        elif step_type == "provider_action":
            await _execute_provider_action(db, run, sr, step, inputs_resolved, claimed_attempt)
        else:
            await _fail_step(
                db,
                run,
                sr,
                "WF_UNKNOWN_STEP_TYPE",
                f"Unknown step type {step_type}",
                claimed_attempt,
            )
    except Exception as exc:
        log.exception("workflow_step_crashed", run_id=run.id, step_id=step["id"])
        await _fail_or_retry(db, run, sr, "WF_STEP_ERROR", str(exc)[:500], claimed_attempt)
    return True


def _run_transform(config: dict, inputs: dict, step: dict) -> dict:
    """Whitelisted transforms only. Phase 1: text ops are real, media ops pass through."""
    op = config.get("operation")
    params = config.get("params", {})
    ports = step.get("outputs", [])
    out_port = ports[0]["port"] if ports else "result"
    # Order values by the step's DECLARED input ports, not dict insertion
    # order. inputs_resolved is keyed in edge-array order — concat_text would
    # otherwise join "a b" or "b a" depending on which edge the author drew
    # first, and select_field's "first input" would silently switch source
    # ports on an unrelated edge edit. Ports without a resolved value are
    # skipped (unconnected optional inputs must not inject None padding);
    # resolved keys not in the declaration (defensive) keep edge order after.
    declared = [p["port"] for p in step.get("inputs", [])]
    values = [inputs[p] for p in declared if p in inputs]
    values += [v for k, v in inputs.items() if k not in declared]
    if op == "concat_text":
        sep = str(params.get("separator", " "))[:10]
        return {out_port: sep.join(str(v) for v in values if v is not None)[:8000]}
    if op == "select_field":
        field = str(params.get("field", ""))
        src = values[0] if values else None
        if isinstance(src, str):
            try:
                src = json.loads(src)
            except (ValueError, TypeError):
                src = None
        if isinstance(src, dict):
            return {out_port: src.get(field)}
        return {out_port: None}
    # crop / resize: pass-through with the operation recorded (no media processing in Phase 1)
    return {out_port: values[0] if values else None, "_operation": op, "_params": params}


async def _complete_step(
    db: AsyncSession,
    run: WorkflowRun,
    sr: WorkflowStepRun,
    output: dict,
    claimed_attempt: int,
) -> None:
    # NUL/control chars in adapter output would crash the JSONB UPDATE
    # (asyncpg UntranslatableCharacterError) and poison the session — the
    # follow-up _fail_or_retry would then double-fault, stranding the step
    # RUNNING with a live lease. Screen BEFORE touching the database.
    if _values_have_ctrl(output):
        await _fail_step(
            db,
            run,
            sr,
            "WF_OUTPUT_INVALID",
            "Step output contains NUL or control characters",
            claimed_attempt,
        )
        return
    if len(json.dumps(output, ensure_ascii=False, default=str)) > MAX_STEP_OUTPUT_BYTES:
        await _fail_step(
            db, run, sr, "WF_OUTPUT_TOO_LARGE", "Step output exceeds 48KB", claimed_attempt
        )
        return
    result = await db.execute(
        update(WorkflowStepRun)
        .where(
            WorkflowStepRun.id == sr.id,
            WorkflowStepRun.status == StepRunStatus.RUNNING,
            WorkflowStepRun.attempt == claimed_attempt,  # fencing token
        )
        .values(
            status=StepRunStatus.COMPLETED,
            output=output,
            finished_at=_now(),
            lease_expires_at=None,
        )
    )
    if result.rowcount:
        db.add(
            WorkflowRunEvent(
                run_id=run.id, step_id=sr.step_id, event_type="step_completed", payload={}
            )
        )


async def _fail_step(
    db: AsyncSession,
    run: WorkflowRun,
    sr: WorkflowStepRun,
    code: str,
    message: str,
    claimed_attempt: int,
) -> None:
    result = await db.execute(
        update(WorkflowStepRun)
        .where(
            WorkflowStepRun.id == sr.id,
            WorkflowStepRun.status == StepRunStatus.RUNNING,
            WorkflowStepRun.attempt == claimed_attempt,  # fencing token
        )
        .values(
            status=StepRunStatus.FAILED,
            error_code=code,
            error=message,
            finished_at=_now(),
            lease_expires_at=None,
        )
    )
    if result.rowcount:
        db.add(
            WorkflowRunEvent(
                run_id=run.id,
                step_id=sr.step_id,
                event_type="step_failed",
                payload={"error_code": code},
            )
        )


async def _fail_or_retry(
    db: AsyncSession,
    run: WorkflowRun,
    sr: WorkflowStepRun,
    code: str,
    message: str,
    claimed_attempt: int,
) -> None:
    """Failed attempt: retry if attempts remain, else FAIL."""
    fresh = await db.get(WorkflowStepRun, sr.id)
    if fresh is None:
        return
    if fresh.attempt < fresh.max_attempts:
        result = await db.execute(
            update(WorkflowStepRun)
            .where(
                WorkflowStepRun.id == sr.id,
                WorkflowStepRun.status == StepRunStatus.RUNNING,
                WorkflowStepRun.attempt == claimed_attempt,  # fencing token
            )
            .values(
                status=StepRunStatus.WAITING_RETRY,
                error_code=code,
                error=message,
                output=None,  # cleared on re-claim (R13)
                lease_expires_at=None,
            )
        )
        if result.rowcount:
            db.add(
                WorkflowRunEvent(
                    run_id=run.id,
                    step_id=sr.step_id,
                    event_type="step_retrying",
                    payload={"attempt": fresh.attempt, "error_code": code},
                )
            )
    else:
        await _fail_step(db, run, sr, code, message, claimed_attempt)


async def _suspend_for_review(
    db: AsyncSession, run: WorkflowRun, sr: WorkflowStepRun, step: dict, claimed_attempt: int
) -> None:
    config = step.get("config", {})
    due_days = min(max(int(config.get("due_days", 7)), 1), 30)
    result = await db.execute(
        update(WorkflowStepRun)
        .where(
            WorkflowStepRun.id == sr.id,
            WorkflowStepRun.status == StepRunStatus.RUNNING,
            WorkflowStepRun.attempt == claimed_attempt,  # fencing token
        )
        .values(status=StepRunStatus.WAITING_REVIEW, lease_expires_at=None)
    )
    if not result.rowcount:
        return
    review = WorkflowStepReview(
        step_run_id=sr.id,
        org_id=run.org_id,
        instructions=(config.get("instructions") or "")[:2000] or None,
        due_at=_now() + timedelta(days=due_days),
    )
    db.add(review)
    db.add(
        WorkflowRunEvent(
            run_id=run.id, step_id=sr.step_id, event_type="review_requested", payload={}
        )
    )
    await db.execute(
        update(WorkflowRun)
        .where(WorkflowRun.id == run.id, WorkflowRun.status == RunStatus.RUNNING)
        .values(status=RunStatus.WAITING_REVIEW)
    )


async def _execute_provider_action(
    db: AsyncSession,
    run: WorkflowRun,
    sr: WorkflowStepRun,
    step: dict,
    inputs_resolved: dict,
    claimed_attempt: int,
) -> None:
    """Execute a provider call with write-ahead idempotency (R13)."""
    from app.core.crypto import decrypt_credentials
    from app.services.workflow_adapters import get_adapter

    config = step.get("config", {})
    capability = config.get("capability", "")

    # Retry pin (R85): once a prior attempt's write-ahead persisted
    # provider_request_id + offering_id, the provider may already have
    # executed (and charged) the work on THAT account — the reused
    # idempotency key only dedupes within a single provider account, so
    # re-running the binding ladder here could silently switch accounts
    # (e.g. a cheaper offering added, or the old connection replaced,
    # between attempts) and re-charge work that already succeeded. Pin the
    # retry to the recorded offering; if it is gone/stale, hard-stop
    # BINDING_STALE — the same no-silent-fallback red line as pinned
    # bindings — never re-resolve onto a different account mid-step.
    if sr.provider_request_id and sr.offering_id:
        offering = await db.get(ProviderModelOffering, sr.offering_id)
        pinned_ok = False
        if offering is not None and offering.is_active:
            conn = await db.get(ProviderConnection, offering.connection_id)
            required = set(config.get("required_features", []))
            pinned_ok = (
                conn is not None
                and conn.org_id == run.org_id
                and conn.status == "active"
                and offering.capability_key == capability
                and required <= set(offering.features or [])
            )
        if not pinned_ok:
            await _fail_step(
                db,
                run,
                sr,
                "BINDING_STALE",
                "Offering recorded by a prior attempt is no longer available; "
                "refusing to switch provider accounts mid-step (idempotency)",
                claimed_attempt,
            )
            return
    else:
        # First attempt: confirmed binding → pinned → auto (first active)
        offering = await _resolve_offering(db, run, step["id"], config)
    if offering is None:
        await _fail_step(
            db,
            run,
            sr,
            "NO_ELIGIBLE_PROVIDER",
            f"No active provider offering for capability '{capability}'",
            claimed_attempt,
        )
        return

    connection = await db.get(ProviderConnection, offering.connection_id)
    if connection is None or connection.status != "active":
        await _fail_step(
            db, run, sr, "BINDING_STALE", "Provider connection is no longer active", claimed_attempt
        )
        return
    adapter_row = await db.get(ProviderAdapter, connection.adapter_id)
    adapter = get_adapter(adapter_row.key) if adapter_row else None
    if adapter is None:
        await _fail_step(
            db, run, sr, "ADAPTER_UNAVAILABLE", "Provider adapter not available", claimed_attempt
        )
        return

    # Write-ahead: persist provider_request_id + offering BEFORE the outbound
    # call (R13). The key is STABLE per step-run and reused across retries /
    # crash recovery — a fresh key each attempt would let a provider that
    # already did the work (crash after the call, before we recorded it)
    # redo/recharge it on the next attempt. Reuse any key persisted by a
    # prior attempt; only mint one the first time.
    provider_request_id = sr.provider_request_id or f"wf-{sr.id}-{secrets.token_hex(6)}"
    write_ahead = await db.execute(
        update(WorkflowStepRun)
        .where(
            WorkflowStepRun.id == sr.id,
            WorkflowStepRun.status == StepRunStatus.RUNNING,
            WorkflowStepRun.attempt == claimed_attempt,  # fencing token
        )
        .values(provider_request_id=provider_request_id, offering_id=offering.id)
    )
    if not write_ahead.rowcount:
        return  # step no longer ours (cancelled / swept) — never call the provider
    await db.commit()  # flush write-ahead state before the call (R13)

    # Post-commit cancellation check: a cancel_run blocked on our row lock may
    # have flipped the step the instant the commit released it. Column SELECT
    # (bypasses the identity map — expire_on_commit=False would otherwise
    # return the stale in-memory object) and bail BEFORE spending provider money.
    fresh_r = await db.execute(
        select(WorkflowStepRun.status, WorkflowStepRun.attempt).where(WorkflowStepRun.id == sr.id)
    )
    fresh = fresh_r.one_or_none()
    if fresh is None or fresh.status != StepRunStatus.RUNNING or fresh.attempt != claimed_attempt:
        return

    # Late credential resolution — only here, never earlier (R3)
    credentials = None
    if connection.credential_id:
        cred = await db.get(OrgCredential, connection.credential_id)
        if cred is not None:
            credentials = decrypt_credentials(cred.encrypted_data)

    # Close the read transaction opened by the freshness/credential SELECTs —
    # otherwise it sits idle-in-transaction for the whole provider call (up to
    # workflow_step_timeout_seconds), holding a pool slot and blocking VACUUM.
    # commit (not rollback): rollback would expire run/sr/offering and the
    # next attribute access would MissingGreenlet; expire_on_commit=False
    # keeps them populated and a read-only commit is a no-op server-side.
    await db.commit()

    try:
        output = await asyncio.wait_for(
            adapter.execute(
                capability=capability,
                model_name=offering.model_name,
                inputs=inputs_resolved,
                config=config,
                credentials=credentials,
                idempotency_key=provider_request_id,
            ),
            timeout=settings.workflow_step_timeout_seconds,
        )
    except TimeoutError:
        await _fail_or_retry(
            db, run, sr, "WF_PROVIDER_TIMEOUT", "Provider call timed out", claimed_attempt
        )
        return
    except Exception as exc:
        await _fail_or_retry(db, run, sr, "WF_PROVIDER_ERROR", str(exc)[:500], claimed_attempt)
        return

    if not isinstance(output, dict):
        output = {"result": str(output)[:8000]}

    # Metering (Issue #27 §3.3a): strip the reserved __usage__ key BEFORE port
    # mapping / _complete_step so it never reaches step output or the 48KB
    # cap. Idempotency key carries the attempt — each real provider call
    # meters once, retries never double-bill.
    usage_items = output.pop("__usage__", None)
    if isinstance(usage_items, list):
        from app.controlplane import facade as cp_facade

        tenant_id = (
            await db.execute(select(Organization.tenant_id).where(Organization.id == run.org_id))
        ).scalar_one_or_none()
        if tenant_id is not None:
            for i, item in enumerate(usage_items):
                try:
                    await cp_facade.emit_usage(
                        db,
                        tenant_id=tenant_id,
                        org_id=run.org_id,
                        usage_type=str(item.get("usage_type", "")),
                        quantity=item.get("quantity", 0),
                        occurred_at=_now(),
                        source="workflow_runtime",
                        idempotency_key=f"wfstep:{sr.id}:{claimed_attempt}:{i}",
                        workflow_run_id=run.id,
                        provider_connection_id=connection.id,
                        provider=adapter_row.key if adapter_row else None,
                        model_or_service=offering.model_name,
                        user_id=run.started_by,
                    )
                except AppError:
                    # A malformed usage element must never fail the step —
                    # the provider work already succeeded. Log and continue.
                    log.warning("wf_usage_emit_rejected", step_run_id=sr.id, item=str(item)[:200])

    # Map adapter output to declared output ports: adapter returns arbitrary
    # keys; declared ports pick matching keys, falling back to "result"
    ports = step.get("outputs", [])
    mapped: dict = {}
    for port in ports:
        mapped[port["port"]] = output.get(port["port"], output.get("result"))
    if not ports:
        mapped = output
    await _complete_step(db, run, sr, mapped, claimed_attempt)


async def _resolve_offering(
    db: AsyncSession, run: WorkflowRun, step_id: str, config: dict
) -> ProviderModelOffering | None:
    """Binding ladder: pinned config → confirmed binding → auto (first active)."""
    capability = config.get("capability", "")

    # Pinned in the definition itself
    pinned_id = config.get("pinned_offering_id")
    if config.get("binding_mode") == "pinned" and pinned_id:
        offering = await db.get(ProviderModelOffering, pinned_id)
        if offering is not None and offering.is_active:
            conn = await db.get(ProviderConnection, offering.connection_id)
            if conn is not None and conn.org_id == run.org_id and conn.status == "active":
                return offering
        return None  # pinned + unavailable = hard stop (allow_fallbacks:false)

    # Org-confirmed binding for this installation+step. Only a row a human
    # actually confirmed counts — install creates UNCONFIRMED suggestion rows
    # (confirmed_by=None, D5) and honoring those would freeze the org on the
    # cheapest-at-install offering forever, making the auto rung dead code.
    if run.installation_id:
        binding_r = await db.execute(
            select(WorkflowStepBinding).where(
                WorkflowStepBinding.installation_id == run.installation_id,
                WorkflowStepBinding.step_id == step_id,
            )
        )
        binding = binding_r.scalar_one_or_none()
        if binding is not None:
            # Pinned offering deleted (FK SET NULL) — hard stop, never a
            # silent fallback to auto-selection (no-auto-assign red line)
            if binding.binding_mode == "pinned" and not binding.offering_id:
                return None
            if binding.confirmed_by is not None and binding.offering_id:
                offering = await db.get(ProviderModelOffering, binding.offering_id)
                if offering is not None and offering.is_active:
                    conn = await db.get(ProviderConnection, offering.connection_id)
                    # Defense-in-depth on the credential path: the binding's
                    # offering must belong to THIS org (R3), serve the step's
                    # CURRENT capability (R82 — an upgrade can change a step's
                    # capability while keeping its id; R78b intentionally KEEPS
                    # the stale confirmed pin as a BINDING_STALE gap, so the
                    # runtime must re-verify capability here or it executes the
                    # wrong-capability offering on the credential path), and
                    # features are mutable — a confirmed offering that no longer
                    # satisfies required_features is stale, not silently good.
                    required = set(config.get("required_features", []))
                    if (
                        conn is not None
                        and conn.org_id == run.org_id
                        and conn.status == "active"
                        and offering.capability_key == capability
                        and required <= set(offering.features or [])
                    ):
                        return offering
                if binding.binding_mode == "pinned":
                    return None  # pinned binding gone stale = hard stop
            # Unconfirmed suggestion rows fall through to the auto rung
            # (which re-runs the cheapest-eligible selection every time)

    # Auto: cheapest active offering for the capability in this org
    result = await db.execute(
        select(ProviderModelOffering)
        .join(ProviderConnection, ProviderConnection.id == ProviderModelOffering.connection_id)
        .where(
            ProviderConnection.org_id == run.org_id,
            ProviderConnection.status == "active",
            ProviderModelOffering.capability_key == capability,
            ProviderModelOffering.is_active.is_(True),
        )
        .order_by(
            ProviderModelOffering.cost_per_call_usd.asc().nullsfirst(),
            ProviderModelOffering.id.asc(),
        )
    )
    offerings = list(result.scalars().all())
    # Feature superset check
    required = set(config.get("required_features", []))
    for off in offerings:
        if required <= set(off.features or []):
            return off
    return None


# ── Sweeper (lazy: run-detail reads + manual endpoint) ────


async def sweep_stale(db: AsyncSession, org_id: str | None = None) -> dict:
    """Recover crashed executors (expired leases) and expire overdue reviews.

    Returns swept counts plus ``run_ids`` — every run touched by the sweep.
    Callers MUST dispatch_advance each returned run_id after commit; sweep
    only repairs step state, it does not resume the advance loop itself.
    """
    now = _now()
    swept: dict = {"expired_leases": 0, "expired_reviews": 0, "stalled_runs": 0, "run_ids": []}
    affected_runs: set[str] = set()

    # Expired leases with attempts remaining → WAITING_RETRY
    retry_q = (
        update(WorkflowStepRun)
        .where(
            WorkflowStepRun.status == StepRunStatus.RUNNING,
            WorkflowStepRun.lease_expires_at.isnot(None),
            WorkflowStepRun.lease_expires_at < now,
            WorkflowStepRun.attempt < WorkflowStepRun.max_attempts,
        )
        .values(
            status=StepRunStatus.WAITING_RETRY,
            error_code="WF_EXECUTOR_CRASHED",
            error="Executor lease expired",
            lease_expires_at=None,
        )
        .returning(WorkflowStepRun.run_id, WorkflowStepRun.step_id, WorkflowStepRun.attempt)
    )
    retry_result = await db.execute(retry_q)
    retry_rows = retry_result.all()
    for run_id, step_id, attempt in retry_rows:
        db.add(
            WorkflowRunEvent(
                run_id=run_id,
                step_id=step_id,
                event_type="step_lease_expired",
                payload={"attempt": attempt, "error_code": "WF_EXECUTOR_CRASHED"},
            )
        )
    affected_runs.update(row[0] for row in retry_rows)
    swept["expired_leases"] += len(retry_rows)

    # Expired leases with attempts exhausted → FAILED (max_attempts must hold
    # on the crash-recovery path too — no unbounded poison-pill retries)
    exhausted_q = (
        update(WorkflowStepRun)
        .where(
            WorkflowStepRun.status == StepRunStatus.RUNNING,
            WorkflowStepRun.lease_expires_at.isnot(None),
            WorkflowStepRun.lease_expires_at < now,
            WorkflowStepRun.attempt >= WorkflowStepRun.max_attempts,
        )
        .values(
            status=StepRunStatus.FAILED,
            error_code="WF_RETRY_EXHAUSTED",
            error="Executor lease expired after final attempt",
            lease_expires_at=None,
            finished_at=now,
        )
        .returning(WorkflowStepRun.run_id, WorkflowStepRun.step_id)
    )
    exhausted_result = await db.execute(exhausted_q)
    exhausted_rows = exhausted_result.all()
    for run_id, step_id in exhausted_rows:
        db.add(
            WorkflowRunEvent(
                run_id=run_id,
                step_id=step_id,
                event_type="step_failed",
                payload={"error_code": "WF_RETRY_EXHAUSTED"},
            )
        )
    affected_runs.update(row[0] for row in exhausted_rows)
    swept["expired_leases"] += len(exhausted_rows)

    # Overdue reviews → expire review (guarded — never overwrite a decision
    # made concurrently by decide_review), fail step, resume the run so the
    # advance loop can propagate SKIPPED and settle it into FAILED
    overdue_q = select(WorkflowStepReview).where(
        WorkflowStepReview.decision.is_(None), WorkflowStepReview.due_at < now
    )
    if org_id:
        overdue_q = overdue_q.where(WorkflowStepReview.org_id == org_id)
    overdue_r = await db.execute(overdue_q)
    for review in overdue_r.scalars().all():
        # Lock the step row FIRST (steps → reviews order, matching cancel_run
        # and decide_review) so the sweeper can't deadlock a concurrent cancel.
        await db.execute(
            select(WorkflowStepRun.id)
            .where(WorkflowStepRun.id == review.step_run_id)
            .with_for_update()
        )
        # Guarded expiry: rowcount 0 = a reviewer decided in the meantime
        expire_result = await db.execute(
            update(WorkflowStepReview)
            .where(
                WorkflowStepReview.id == review.id,
                WorkflowStepReview.decision.is_(None),
            )
            .values(decision="expired", decided_at=now)
        )
        if not expire_result.rowcount:
            continue
        fail_result = await db.execute(
            update(WorkflowStepRun)
            .where(
                WorkflowStepRun.id == review.step_run_id,
                WorkflowStepRun.status == StepRunStatus.WAITING_REVIEW,
            )
            .values(
                status=StepRunStatus.FAILED,
                error_code="WF_REVIEW_TIMEOUT",
                error="Review was not decided before its due date",
                finished_at=now,
            )
        )
        step_run = await db.get(WorkflowStepRun, review.step_run_id)
        if step_run is not None:
            db.add(
                WorkflowRunEvent(
                    run_id=step_run.run_id,
                    step_id=step_run.step_id,
                    event_type="review_expired",
                    payload={},
                )
            )
            # Guarded like every settlement: only record step_failed when THIS
            # sweep actually flipped the step (a concurrent cancel loses cleanly)
            if fail_result.rowcount:
                db.add(
                    WorkflowRunEvent(
                        run_id=step_run.run_id,
                        step_id=step_run.step_id,
                        event_type="step_failed",
                        payload={"error_code": "WF_REVIEW_TIMEOUT"},
                    )
                )
            # Move the run out of WAITING_REVIEW so the advance loop (which
            # only progresses RUNNING runs) can settle it
            await db.execute(
                update(WorkflowRun)
                .where(
                    WorkflowRun.id == step_run.run_id,
                    WorkflowRun.status == RunStatus.WAITING_REVIEW,
                )
                .values(status=RunStatus.RUNNING)
            )
            affected_runs.add(step_run.run_id)
        swept["expired_reviews"] += 1

    # Stalled-run recovery (R73): a run left in PENDING/RUNNING with NO live
    # executor — no step RUNNING under an unexpired lease — is never touched by
    # the lease-expiry or review queries above. This happens on a crash/deploy
    # between create_run's commit and dispatch_advance, or when a task is
    # drained at shutdown, leaving the run PENDING (steps all PENDING) or
    # RUNNING (a step committed WAITING_RETRY, whose lease was cleared to None).
    # The lazy per-read redispatch recovers such a run only if someone VIEWS
    # it; nobody's runs would otherwise recover via the cron/admin path, and
    # they count toward workflow_max_concurrent_runs → permanent 422
    # WF_TOO_MANY_ACTIVE_RUNS. Re-dispatch is idempotent (advance_run uses
    # conditional status-guarded claims), so surfacing these run_ids is safe.
    # A grace window avoids racing a just-created run whose dispatch is still
    # in flight. No status write here — advance_run makes the transition.
    grace = now - timedelta(seconds=settings.workflow_step_timeout_seconds)
    live_lease = (
        select(WorkflowStepRun.run_id)
        .where(
            WorkflowStepRun.status == StepRunStatus.RUNNING,
            WorkflowStepRun.lease_expires_at.isnot(None),
            WorkflowStepRun.lease_expires_at >= now,
        )
        .scalar_subquery()
    )
    stalled_q = select(WorkflowRun.id).where(
        WorkflowRun.status.in_([RunStatus.PENDING, RunStatus.RUNNING]),
        WorkflowRun.created_at < grace,
        WorkflowRun.id.notin_(live_lease),
    )
    if org_id:
        stalled_q = stalled_q.where(WorkflowRun.org_id == org_id)
    stalled_r = await db.execute(stalled_q)
    # Exclude runs the lease/review passes above already recovered THIS sweep
    # (a review-expired run is flipped to RUNNING with no live lease, so the
    # stalled predicate re-selects it) — else the same run inflates BOTH
    # counters and operators can't trust stalled_runs as an orphan count (R78).
    stalled_ids = [row[0] for row in stalled_r.all() if row[0] not in affected_runs]
    if stalled_ids:
        affected_runs.update(stalled_ids)
        swept["stalled_runs"] = len(stalled_ids)

    await db.flush()
    swept["run_ids"] = sorted(affected_runs)
    return swept
