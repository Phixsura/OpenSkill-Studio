"""Benchmark Lab (ADR-016 Part F).

Runs execute suite cases against a target via a pluggable executor (mock in
tests). Budget caps abort runs; aggregation preserves every score dimension —
there is deliberately no universal quality score.
"""

import statistics
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.benchmark import (
    BENCHMARK_FAMILIES,
    BenchmarkCase,
    BenchmarkResult,
    BenchmarkReview,
    BenchmarkRun,
    BenchmarkSuite,
)
from app.ecosystem.security import sanitize_text
from app.exceptions import AppError


async def latest_completed_run(
    db: AsyncSession, entity_kind: str, entity_id: str
) -> BenchmarkRun | None:
    """Latest completed run targeting one entity (None when never benchmarked)."""
    runs = await db.scalars(
        select(BenchmarkRun)
        .where(BenchmarkRun.status == "completed")
        .order_by(BenchmarkRun.finished_at.desc())
        .limit(200)
    )
    for run in runs:
        target = run.target or {}
        if target.get("entity_kind") == entity_kind and target.get("entity_id") == entity_id:
            return run
    return None


async def latest_dimension_scores(db: AsyncSession, entity_kind: str, entity_id: str) -> dict:
    """Latest completed run's dimension scores for one target entity."""
    run = await latest_completed_run(db, entity_kind, entity_id)
    return dict(run.dimension_scores or {}) if run else {}



def _cases_fingerprint(cases: list) -> str:
    """Deterministic hash over the case set (id, prompt, weight, constraints) —
    HELM-style suite versioning: a run is bound to the exact case set it saw."""
    import hashlib
    import json

    basis = [
        {
            "id": c.id,
            "prompt": c.prompt,
            "weight": float(c.weight or 1.0),
            "constraints": c.constraints or {},
        }
        for c in sorted(cases, key=lambda c: c.id)
    ]
    return hashlib.sha256(json.dumps(basis, sort_keys=True, default=str).encode()).hexdigest()


class OfferingExecutor:
    """Executes cases against a REAL ProviderModelOffering through the
    platform's provider-adapter chain (same contract as the workflow runtime:
    late credential resolution, stable idempotency key per case×repeat,
    bounded call timeout). Selected automatically when the run target names
    an `offering_id` — this is what makes the Benchmark Lab able to measure
    actual providers, not just mocks (Replicate/AA-grade realness).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_case(self, run: "BenchmarkRun", case: "BenchmarkCase", repeat: int) -> dict:
        import asyncio
        import time

        from app.config import settings
        from app.core.crypto import decrypt_credentials
        from app.models.provider import (
            OrgCredential,
            ProviderAdapter,
            ProviderConnection,
            ProviderModelOffering,
        )
        from app.services.workflow_adapters import get_adapter

        offering_id = (run.target or {}).get("offering_id")
        offering = await self.db.get(ProviderModelOffering, offering_id) if offering_id else None
        if offering is None or not offering.is_active:
            raise RuntimeError("BENCH_OFFERING_UNAVAILABLE: offering missing or inactive")
        connection = await self.db.get(ProviderConnection, offering.connection_id)
        if connection is None or connection.status != "active":
            raise RuntimeError("BENCH_CONNECTION_INACTIVE: provider connection not active")
        adapter_row = await self.db.get(ProviderAdapter, connection.adapter_id)
        adapter = get_adapter(adapter_row.key) if adapter_row else None
        if adapter is None:
            raise RuntimeError("BENCH_ADAPTER_UNAVAILABLE: provider adapter not available")
        # Late credential resolution — same posture as the runtime (R3)
        credentials = None
        if connection.credential_id:
            cred = await self.db.get(OrgCredential, connection.credential_id)
            if cred is not None:
                credentials = decrypt_credentials(cred.encrypted_data)
        inputs = {
            "prompt": case.prompt,
            "constraints": case.constraints or {},
            "reference_assets": case.reference_assets or [],
            "seed_settings": run.seed_settings or {},
            "repeat_index": repeat,
        }
        # Stable per case×repeat: a crashed executor retrying never double-bills
        idempotency_key = f"bench-{run.id}-{case.id}-{repeat}"
        started = time.monotonic()
        output = await asyncio.wait_for(
            adapter.execute(
                capability=offering.capability_key,
                model_name=offering.model_name,
                inputs=inputs,
                config=connection.config or {},
                credentials=credentials,
                idempotency_key=idempotency_key,
            ),
            timeout=settings.workflow_step_timeout_seconds,
        )
        latency_ms = int((time.monotonic() - started) * 1000)
        usage = output.pop("__usage__", []) if isinstance(output, dict) else []
        result_ref = output.get("result") if isinstance(output, dict) else None
        return {
            "output_assets": (
                [{"kind": "provider_output", "ref": str(result_ref)[:500]}] if result_ref else []
            ),
            "latency_ms": latency_ms,
            "usage": {"events": usage},
            "cost_usd": float(offering.cost_per_call_usd or 0),
            "automated_scores": {},
            "failed": False,
            "retries": 0,
        }


class MockExecutor:
    """Deterministic executor for tests/dev: derives outputs from the seed."""

    async def execute_case(self, run: BenchmarkRun, case: BenchmarkCase, repeat: int) -> dict:
        seed = f"{run.id}:{case.id}:{repeat}"
        h = sum(ord(c) for c in seed)
        return {
            "output_assets": [{"kind": "image", "ref": f"mock://{seed}"}],
            "latency_ms": 500 + (h % 1500),
            "usage": {"images": 1},
            "cost_usd": round(0.01 + (h % 10) / 1000, 6),
            "automated_scores": {"text_accuracy": round(0.7 + (h % 30) / 100, 3)},
            "failed": False,
            "retries": 0,
        }


class BenchmarkService:
    def __init__(self, db: AsyncSession, executor=None):
        self.db = db
        # None = auto-select at execute time: OfferingExecutor when the run
        # targets a real offering, MockExecutor otherwise
        self.executor = executor

    def _resolve_executor(self, run: "BenchmarkRun"):
        if self.executor is not None:
            return self.executor
        if (run.target or {}).get("offering_id"):
            return OfferingExecutor(self.db)
        return MockExecutor()

    # ── Suites & cases ──────────────────────────────────────────────

    async def create_suite(
        self,
        *,
        key: str,
        name: str,
        family: str,
        capability_key: str,
        description: str | None = None,
        rubric: list | None = None,
        human_review_policy: dict | None = None,
        automated_metrics: list | None = None,
        budget_usd_cap: float = 10.0,
        repeat_count: int = 3,
        created_by: str | None = None,
    ) -> BenchmarkSuite:
        if family not in BENCHMARK_FAMILIES:
            raise AppError("VALIDATION_ERROR", f"Unknown benchmark family: {family}", 422)
        if not 1 <= repeat_count <= 10:
            raise AppError("VALIDATION_ERROR", "repeat_count must be 1..10", 422)
        if await self.db.scalar(select(BenchmarkSuite).where(BenchmarkSuite.key == key)):
            raise AppError("ECO_SUITE_EXISTS", "Suite key already exists", 409)
        suite = BenchmarkSuite(
            key=key,
            name=name,
            family=family,
            capability_key=capability_key,
            description=sanitize_text(description, 2000),
            rubric=rubric or [],
            human_review_policy=human_review_policy or {"required": True, "blind": True, "min_reviewers": 2},
            automated_metrics=automated_metrics or [],
            budget_usd_cap=budget_usd_cap,
            repeat_count=repeat_count,
            created_by=created_by,
        )
        self.db.add(suite)
        await self.db.flush()
        return suite

    async def get_suite(self, suite_id: str) -> BenchmarkSuite:
        suite = await self.db.get(BenchmarkSuite, suite_id)
        if not suite:
            raise AppError("NOT_FOUND", "Suite not found", 404)
        return suite

    async def list_suites(
        self, *, family: str | None = None, status: str | None = None, limit: int = 50
    ) -> list[BenchmarkSuite]:
        query = select(BenchmarkSuite)
        if family:
            query = query.where(BenchmarkSuite.family == family)
        if status:
            query = query.where(BenchmarkSuite.status == status)
        rows = await self.db.scalars(query.order_by(BenchmarkSuite.created_at.desc()).limit(limit))
        return list(rows)

    async def update_suite(self, suite_id: str, updates: dict) -> BenchmarkSuite:
        suite = await self.get_suite(suite_id)
        allowed = {
            "name", "description", "rubric", "human_review_policy",
            "automated_metrics", "budget_usd_cap", "repeat_count", "status",
        }
        for key, value in updates.items():
            if key not in allowed:
                continue
            if key == "status" and value not in ("draft", "active", "archived"):
                raise AppError("VALIDATION_ERROR", f"Unknown status: {value}", 422)
            setattr(suite, key, value)
        await self.db.flush()
        return suite

    async def add_case(
        self,
        suite_id: str,
        *,
        name: str,
        prompt: str,
        reference_assets: list | None = None,
        constraints: dict | None = None,
        weight: float = 1.0,
        sort_order: int = 0,
    ) -> BenchmarkCase:
        await self.get_suite(suite_id)
        case = BenchmarkCase(
            suite_id=suite_id,
            name=name,
            prompt=prompt,
            reference_assets=reference_assets or [],
            constraints=constraints or {},
            weight=weight,
            sort_order=sort_order,
        )
        self.db.add(case)
        await self.db.flush()
        return case

    SUITE_EXPORT_VERSION = 1

    async def export_suite(self, suite_id: str) -> dict:
        """HELM portable-suite bar: a self-contained, versioned JSON document
        (definition + cases + fingerprint) that another deployment can import.
        Runs/results are never exported — they belong to the environment that
        produced them."""
        suite = await self.get_suite(suite_id)
        cases = await self.list_cases(suite_id)
        return {
            "format": "openskill.benchmark-suite",
            "version": self.SUITE_EXPORT_VERSION,
            "suite": {
                "key": suite.key,
                "name": suite.name,
                "family": suite.family,
                "capability_key": suite.capability_key,
                "description": suite.description,
                "rubric": suite.rubric or [],
                "human_review_policy": suite.human_review_policy or {},
                "automated_metrics": suite.automated_metrics or [],
                "budget_usd_cap": float(suite.budget_usd_cap),
                "repeat_count": suite.repeat_count,
            },
            "cases": [
                {
                    "name": c.name,
                    "prompt": c.prompt,
                    "reference_assets": c.reference_assets or [],
                    "constraints": c.constraints or {},
                    "weight": float(c.weight or 1.0),
                    "sort_order": c.sort_order,
                }
                for c in cases
            ],
            "cases_fingerprint": _cases_fingerprint(cases),
        }

    async def import_suite(self, document: dict, *, created_by: str) -> BenchmarkSuite:
        """Import an exported suite document. Untrusted content: bounded,
        sanitized, validated by the same paths as manual creation; the suite
        arrives in draft status and key collisions are rejected (never
        silently merged)."""
        if not isinstance(document, dict) or document.get("format") != "openskill.benchmark-suite":
            raise AppError("VALIDATION_ERROR", "Not a benchmark-suite export document", 422)
        if document.get("version") != self.SUITE_EXPORT_VERSION:
            raise AppError("VALIDATION_ERROR", "Unsupported suite export version", 422)
        spec = document.get("suite")
        cases = document.get("cases")
        if not isinstance(spec, dict) or not isinstance(cases, list) or not cases:
            raise AppError("VALIDATION_ERROR", "Export must carry a suite and 1+ cases", 422)
        if len(cases) > 200:
            raise AppError("VALIDATION_ERROR", "At most 200 cases per import", 422)
        from app.ecosystem.schemas import CreateCaseRequest, CreateSuiteRequest

        try:
            suite_req = CreateSuiteRequest(
                **{k: spec.get(k) for k in CreateSuiteRequest.model_fields if spec.get(k) is not None}
            )
            case_reqs = [
                CreateCaseRequest(
                    **{k: c.get(k) for k in CreateCaseRequest.model_fields if isinstance(c, dict) and c.get(k) is not None}
                )
                for c in cases
            ]
        except Exception as exc:  # noqa: BLE001 — pydantic detail surfaced as 422
            raise AppError("VALIDATION_ERROR", f"Invalid suite document: {exc}", 422) from None
        suite = await self.create_suite(created_by=created_by, **suite_req.model_dump())
        for case_req in case_reqs:
            await self.add_case(suite.id, **case_req.model_dump())
        return suite

    async def list_cases(self, suite_id: str) -> list[BenchmarkCase]:
        rows = await self.db.scalars(
            select(BenchmarkCase)
            .where(BenchmarkCase.suite_id == suite_id)
            .order_by(BenchmarkCase.sort_order)
        )
        return list(rows)

    # ── Runs ────────────────────────────────────────────────────────

    async def create_run(
        self,
        suite_id: str,
        *,
        target: dict,
        budget_usd_cap: float | None = None,
        seed_settings: dict | None = None,
        triggered_by: str | None = None,
    ) -> BenchmarkRun:
        suite = await self.get_suite(suite_id)
        if suite.status != "active":
            raise AppError("VALIDATION_ERROR", "Suite must be active to run", 422)
        if not isinstance(target, dict) or not target.get("entity_kind"):
            raise AppError("VALIDATION_ERROR", "Run target must name an entity", 422)
        cases = await self.list_cases(suite_id)
        run = BenchmarkRun(
            suite_id=suite_id,
            target=target,
            budget_usd_cap=budget_usd_cap or suite.budget_usd_cap,
            seed_settings=seed_settings or {},
            environment_snapshot={
                "executor": (
                    type(self.executor).__name__
                    if self.executor is not None
                    else ("OfferingExecutor" if target.get("offering_id") else "MockExecutor")
                ),
                "suite_key": suite.key,
                # §13 suite versioning: the run is pinned to this exact case
                # set; execute refuses to run against a drifted suite
                "suite_snapshot": {
                    "cases_fingerprint": _cases_fingerprint(cases),
                    "case_count": len(cases),
                    "repeat_count": suite.repeat_count,
                    "rubric": suite.rubric,
                },
            },
            triggered_by=triggered_by,
        )
        self.db.add(run)
        await self.db.flush()
        return run

    async def execute_run(self, run_id: str) -> BenchmarkRun:
        """Execute all case × repeat combinations, respecting the budget cap."""
        run = await self.db.get(BenchmarkRun, run_id)
        if not run:
            raise AppError("NOT_FOUND", "Run not found", 404)
        if run.status not in ("queued",):
            raise AppError("ECO_INVALID_TRANSITION", f"Run is {run.status}, not queued", 409)
        # §16 fencing (workflow-runtime discipline): claim the run with a
        # conditional UPDATE so two workers can never double-execute (and
        # double-bill) the same run — the loser sees rowcount 0 and walks away.
        from sqlalchemy import update

        claim = await self.db.execute(
            update(BenchmarkRun)
            .where(BenchmarkRun.id == run_id, BenchmarkRun.status == "queued")
            .values(status="running", started_at=datetime.now(UTC))
        )
        if not claim.rowcount:
            raise AppError(
                "ECO_INVALID_TRANSITION", "Run was claimed by another worker", 409
            )
        await self.db.flush()
        suite = await self.get_suite(run.suite_id)
        cases = await self.list_cases(run.suite_id)
        if not cases:
            run.status = "failed"
            run.error = "Suite has no cases"
            await self.db.flush()
            return run
        snapshot = (run.environment_snapshot or {}).get("suite_snapshot")
        if snapshot and snapshot.get("cases_fingerprint") != _cases_fingerprint(cases):
            # HELM lesson: results must correspond to the recorded suite. A
            # suite edited between queue and execute invalidates the run
            # rather than silently measuring something else.
            run.status = "failed"
            run.error = "ECO_SUITE_DRIFT: suite cases changed since the run was created"
            run.finished_at = datetime.now(UTC)
            await self.db.flush()
            return run
        run.status = "running"  # keep the in-memory object aligned with the claim
        executor = self._resolve_executor(run)

        total_cost = Decimal("0")
        budget = Decimal(str(run.budget_usd_cap))
        aborted = False
        for case in cases:
            for repeat in range(suite.repeat_count):
                if total_cost >= budget:
                    aborted = True
                    break
                try:
                    outcome = await executor.execute_case(run, case, repeat)
                except Exception as exc:  # noqa: BLE001 — provider failures are data
                    outcome = {
                        "output_assets": [],
                        "latency_ms": None,
                        "usage": {},
                        "cost_usd": 0,
                        "automated_scores": {},
                        "failed": True,
                        "retries": 0,
                        "error": sanitize_text(str(exc), 500),
                    }
                cost = Decimal(str(outcome.get("cost_usd", 0)))
                total_cost += cost
                self.db.add(
                    BenchmarkResult(
                        run_id=run.id,
                        case_id=case.id,
                        repeat_index=repeat,
                        input_snapshot={"prompt": case.prompt, "constraints": case.constraints},
                        output_assets=outcome.get("output_assets", []),
                        latency_ms=outcome.get("latency_ms"),
                        usage=outcome.get("usage", {}),
                        cost_usd=cost,
                        retries=outcome.get("retries", 0),
                        failed=outcome.get("failed", False),
                        error=outcome.get("error"),
                        automated_scores=outcome.get("automated_scores", {}),
                    )
                )
            if aborted:
                break
        run.total_cost_usd = total_cost
        await self.db.flush()
        if aborted:
            run.status = "failed"
            run.error = "ECO_BUDGET_EXCEEDED: run aborted at budget cap"
            run.finished_at = datetime.now(UTC)
            await self.db.flush()
            return run
        run.dimension_scores = await self._aggregate(run)
        run.status = "completed"
        run.finished_at = datetime.now(UTC)
        await self.db.flush()
        await self._detect_regression(run)
        await self._check_production_divergence(run)
        return run

    async def _check_production_divergence(self, run: BenchmarkRun) -> None:
        """§3.7 both directions: a fresh benchmark is immediately compared to
        the latest cross-tenant production telemetry for the same target."""
        from app.ecosystem.services.telemetry import TelemetryService

        target = run.target or {}
        entity_id = target.get("entity_id")
        entity_kind = target.get("entity_kind")
        if not entity_id or not entity_kind:
            return
        scores = dict(run.dimension_scores or {})
        scores.pop("dimension_stats", None)
        await TelemetryService(self.db).detect_divergence(
            entity_kind, entity_id, benchmark_scores=scores
        )

    # Lower-is-better dimensions: a significant INCREASE is the regression
    _LOWER_BETTER_DIMS = frozenset({"cost_usd", "latency_ms"})

    async def _detect_regression(self, run: BenchmarkRun) -> None:
        """promptfoo/LangSmith CI bar: compare this completed run against the
        PREVIOUS completed run for the same suite + target; any dimension that
        significantly worsened (Welch p<0.05 on summary stats) emits a typed
        `degraded` change event on the internal benchmark source. Detection
        only — no auto-rollback, no lifecycle mutation (safety posture)."""
        from app.ecosystem.services.stats import welch_t_from_stats

        target = run.target or {}
        entity_id = target.get("entity_id")
        if not entity_id:
            return
        previous = None
        older = await self.db.scalars(
            select(BenchmarkRun)
            .where(
                BenchmarkRun.suite_id == run.suite_id,
                BenchmarkRun.status == "completed",
                BenchmarkRun.id != run.id,
            )
            .order_by(BenchmarkRun.finished_at.desc())
            .limit(100)
        )
        for candidate in older:
            if (candidate.target or {}).get("entity_id") == entity_id:
                previous = candidate
                break
        if previous is None:
            return
        new_stats = (run.dimension_scores or {}).get("dimension_stats") or {}
        old_stats = (previous.dimension_scores or {}).get("dimension_stats") or {}
        regressions = []
        for dim, ns in new_stats.items():
            os_ = old_stats.get(dim)
            if not isinstance(ns, dict) or not isinstance(os_, dict):
                continue
            try:
                p_value = welch_t_from_stats(
                    float(ns["mean"]), float(ns.get("std", 0)), int(ns.get("n", 0)),
                    float(os_["mean"]), float(os_.get("std", 0)), int(os_.get("n", 0)),
                )
            except (KeyError, TypeError, ValueError):
                continue
            worse = (
                ns["mean"] > os_["mean"]
                if dim in self._LOWER_BETTER_DIMS
                else ns["mean"] < os_["mean"]
            )
            if worse and p_value < 0.05:
                regressions.append(
                    {
                        "dimension": dim,
                        "old_mean": os_["mean"],
                        "new_mean": ns["mean"],
                        "p_value": p_value,
                    }
                )
        if not regressions:
            return
        import hashlib

        from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
        from app.ecosystem.models.source import EcosystemSource
        from app.ecosystem.services.change_detection import _fanout

        source = await self.db.scalar(
            select(EcosystemSource).where(EcosystemSource.name == "internal:benchmark-lab")
        )
        if source is None:
            source = EcosystemSource(
                name="internal:benchmark-lab",
                source_type="internal_research",
                trust_level="internal",
                adapter_key="manual",
                parser_version="1.0",
                robots_compliant=True,
            )
            self.db.add(source)
            await self.db.flush()
        obs = EcosystemObservation(
            source_id=source.id,
            event_type="benchmark_published",
            entity_kind=target.get("entity_kind"),
            canonical_entity_kind=target.get("entity_kind"),
            canonical_entity_id=entity_id,
            raw_hash=hashlib.sha256(f"regression:{run.id}".encode()).hexdigest(),
            normalized={"run_id": run.id, "previous_run_id": previous.id,
                        "regressions": regressions},
            extraction_method="structured",
        )
        self.db.add(obs)
        await self.db.flush()
        change = ChangeEvent(
            observation_id=obs.id,
            change_type="benchmark",
            field="benchmark_regression",
            old_value={"run_id": previous.id},
            new_value={"run_id": run.id, "regressions": regressions},
            severity="degraded",
            entity_kind=target.get("entity_kind"),
            canonical_entity_id=entity_id,
        )
        self.db.add(change)
        await self.db.flush()
        _fanout(self.db, change)
        await self.db.flush()

    async def _aggregate(self, run: BenchmarkRun) -> dict:
        """Aggregate results into preserved per-dimension scores.

        World-class posture (HELM/AA): case weights are honored, and every
        aggregated dimension carries uncertainty (std, n, 95% CI) in a
        parallel `dimension_stats` key — the point value stays in
        `dimension_scores` for backward-compatible ranking/compare flows.
        """
        from app.ecosystem.services.stats import mean_ci95, weighted_mean

        results = await self.db.scalars(
            select(BenchmarkResult).where(BenchmarkResult.run_id == run.id)
        )
        results = list(results)
        if not results:
            return {}
        case_weight: dict[str, float] = {
            c.id: float(c.weight or 1.0) for c in await self.list_cases(run.suite_id)
        }

        def w(result) -> float:
            return case_weight.get(result.case_id, 1.0)

        latencies = [r.latency_ms for r in results if r.latency_ms is not None]
        costs = [float(r.cost_usd or 0) for r in results]
        success_flags = [(0.0 if r.failed else 1.0, w(r)) for r in results]
        dims: dict = {
            "reliability": round(weighted_mean(success_flags), 4),
            "speed_p50_ms": statistics.median(latencies) if latencies else None,
            "cost_per_case_usd": round(sum(costs) / len(results), 6),
        }
        stats_out: dict = {
            "latency_ms": mean_ci95([float(v) for v in latencies]),
            "cost_usd": mean_ci95(costs),
            "reliability": mean_ci95([flag for flag, _ in success_flags]),
        }
        # Automated metrics: weighted point value + CI per dimension
        metric_values: dict[str, list[tuple[float, float]]] = {}
        for r in results:
            for key, value in (r.automated_scores or {}).items():
                if isinstance(value, (int, float)) and value == value:
                    metric_values.setdefault(key, []).append((float(value), w(r)))
        for key, pairs in metric_values.items():
            dims[key] = round(weighted_mean(pairs), 4)
            stats_out[key] = mean_ci95([v for v, _ in pairs])
        # Human-review dimensions merge in after blind reveal (see blind_review)
        human, human_stats = await self._human_dimensions(run.id)
        dims.update(human)
        stats_out.update(human_stats)
        dims["dimension_stats"] = stats_out
        return dims

    async def _human_dimensions(self, run_id: str) -> tuple[dict, dict]:
        from app.ecosystem.services.stats import mean_ci95

        reviews = await self.db.scalars(
            select(BenchmarkReview).where(
                BenchmarkReview.run_id == run_id,
                BenchmarkReview.submitted_at.isnot(None),
            )
        )
        buckets: dict[str, list[float]] = {}
        for review in reviews:
            for dim, score in (review.scores or {}).items():
                if isinstance(score, (int, float)) and score == score:
                    buckets.setdefault(dim, []).append(float(score))
        dims = {dim: round(sum(v) / len(v), 4) for dim, v in buckets.items()}
        stats_out = {dim: mean_ci95(v) for dim, v in buckets.items()}
        return dims, stats_out

    async def refresh_dimensions(self, run_id: str) -> BenchmarkRun:
        """Re-aggregate after human reviews land (post-reveal)."""
        run = await self.db.get(BenchmarkRun, run_id)
        if not run:
            raise AppError("NOT_FOUND", "Run not found", 404)
        run.dimension_scores = await self._aggregate(run)
        await self.db.flush()
        return run

    async def cancel_run(self, run_id: str, *, actor_id: str | None = None) -> BenchmarkRun:
        """§17: cancel a queued run (fence-aware conditional UPDATE, so a
        cancel racing an executor claim has exactly one winner). Running runs
        are cancel-requested by the same fence: the executor's claim already
        succeeded, so cancellation of RUNNING is refused — budget caps bound
        the remaining spend (matches the runtime's cancel-before-spend rule).
        """
        from sqlalchemy import update

        run = await self.db.get(BenchmarkRun, run_id)
        if not run:
            raise AppError("NOT_FOUND", "Run not found", 404)
        claimed = await self.db.execute(
            update(BenchmarkRun)
            .where(BenchmarkRun.id == run_id, BenchmarkRun.status == "queued")
            .values(status="cancelled", finished_at=datetime.now(UTC))
        )
        if not claimed.rowcount:
            raise AppError(
                "ECO_INVALID_TRANSITION",
                f"Run is {run.status}; only queued runs can be cancelled",
                409,
            )
        await self.db.flush()
        await self.db.refresh(run)
        return run

    async def get_run(self, run_id: str) -> BenchmarkRun:
        run = await self.db.get(BenchmarkRun, run_id)
        if not run:
            raise AppError("NOT_FOUND", "Run not found", 404)
        return run

    async def list_runs(
        self, *, suite_id: str | None = None, status: str | None = None, limit: int = 50
    ) -> list[BenchmarkRun]:
        query = select(BenchmarkRun)
        if suite_id:
            query = query.where(BenchmarkRun.suite_id == suite_id)
        if status:
            query = query.where(BenchmarkRun.status == status)
        rows = await self.db.scalars(query.order_by(BenchmarkRun.created_at.desc()).limit(limit))
        return list(rows)

    async def list_results(self, run_id: str) -> list[BenchmarkResult]:
        rows = await self.db.scalars(
            select(BenchmarkResult)
            .where(BenchmarkResult.run_id == run_id)
            .order_by(BenchmarkResult.case_id, BenchmarkResult.repeat_index)
        )
        return list(rows)

    async def leaderboard(
        self,
        *,
        family: str | None = None,
        suite_id: str | None = None,
        dimension: str = "reliability",
        limit: int = 50,
    ) -> dict:
        """LMArena/AA-style leaderboard: the LATEST completed run per unique
        target entity across the family's suites, rankable by any preserved
        dimension. One row per entity — dimensions never collapsed; each row
        carries the full dimension set + uncertainty so the UI can re-sort
        client-side without re-fetching.
        """
        query = select(BenchmarkRun).where(BenchmarkRun.status == "completed")
        if suite_id:
            query = query.where(BenchmarkRun.suite_id == suite_id)
        elif family:
            suite_ids = [
                s.id
                for s in await self.db.scalars(
                    select(BenchmarkSuite).where(BenchmarkSuite.family == family)
                )
            ]
            if not suite_ids:
                return {"dimension": dimension, "rows": []}
            query = query.where(BenchmarkRun.suite_id.in_(suite_ids))
        runs = await self.db.scalars(
            query.order_by(BenchmarkRun.finished_at.desc()).limit(500)
        )
        latest_per_target: dict[tuple, BenchmarkRun] = {}
        for run in runs:
            target = run.target or {}
            key = (target.get("entity_kind"), target.get("entity_id"))
            if key[1] and key not in latest_per_target:
                latest_per_target[key] = run
        from app.ecosystem.models.catalog import CATALOG_KIND_TO_MODEL

        rows: list[dict] = []
        for (entity_kind, entity_id), run in latest_per_target.items():
            name = entity_id
            model = CATALOG_KIND_TO_MODEL.get(entity_kind)
            if model is not None:
                entity = await self.db.get(model, entity_id)
                if entity is not None:
                    name = entity.canonical_name
            scores = dict(run.dimension_scores or {})
            stats_blob = scores.pop("dimension_stats", {})
            rows.append(
                {
                    "entity_kind": entity_kind,
                    "entity_id": entity_id,
                    "canonical_name": name,
                    "run_id": run.id,
                    "suite_id": run.suite_id,
                    "finished_at": run.finished_at,
                    "total_cost_usd": float(run.total_cost_usd or 0),
                    "dimension_scores": scores,
                    "dimension_stats": stats_blob,
                }
            )
        # Rank: lower-is-better for cost/latency dims, higher otherwise;
        # entities missing the dimension sort last, never hidden
        lower_is_better = dimension in ("cost_per_case_usd", "speed_p50_ms")

        def sort_key(row: dict):
            value = row["dimension_scores"].get(dimension)
            missing = value is None or not isinstance(value, (int, float))
            if missing:
                return (1, 0.0)
            return (0, float(value) if lower_is_better else -float(value))

        rows.sort(key=sort_key)
        rows = rows[:limit]
        # Pareto frontier (Artificial-Analysis style quality-vs-cost): a row is
        # on the frontier when NO other row has strictly better quality AND
        # strictly lower cost. Only computed for higher-is-better dimensions
        # with a usable cost; rows without both stay unflagged, never hidden.
        if not lower_is_better:
            scored = [
                (i, float(r["dimension_scores"][dimension]), r["total_cost_usd"])
                for i, r in enumerate(rows)
                if isinstance(r["dimension_scores"].get(dimension), (int, float))
                and r["total_cost_usd"] > 0
            ]
            for i, quality, cost in scored:
                dominated = any(
                    q2 > quality and c2 < cost for j, q2, c2 in scored if j != i
                )
                rows[i]["on_frontier"] = not dominated
        return {"dimension": dimension, "rows": rows}

    async def score_history(
        self,
        *,
        entity_kind: str,
        entity_id: str,
        dimension: str = "reliability",
        suite_id: str | None = None,
    ) -> dict:
        """LMArena score-over-time bar: chronological series of one dimension
        across an entity's completed runs (+ linear trend, advisory). Suites
        are not mixed unless explicitly unfiltered — each point carries its
        suite_id so the UI can facet."""
        from app.ecosystem.services.stats import linear_trend

        query = (
            select(BenchmarkRun)
            .where(BenchmarkRun.status == "completed")
            .order_by(BenchmarkRun.finished_at.asc())
            .limit(500)
        )
        if suite_id:
            query = query.where(BenchmarkRun.suite_id == suite_id)
        points = []
        for run in await self.db.scalars(query):
            target = run.target or {}
            if (
                target.get("entity_kind") != entity_kind
                or target.get("entity_id") != entity_id
            ):
                continue
            value = (run.dimension_scores or {}).get(dimension)
            if not isinstance(value, (int, float)):
                continue
            points.append(
                {
                    "run_id": run.id,
                    "suite_id": run.suite_id,
                    "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                    "value": float(value),
                }
            )
        trend = None
        usable = [p2 for p2 in points if p2["finished_at"]]
        if len(usable) >= 2:
            base = datetime.fromisoformat(usable[0]["finished_at"])
            xy = [
                (
                    (datetime.fromisoformat(p2["finished_at"]) - base).total_seconds()
                    / 86400.0,
                    p2["value"],
                )
                for p2 in usable
            ]
            trend = linear_trend(xy)
        return {
            "entity_kind": entity_kind,
            "entity_id": entity_id,
            "dimension": dimension,
            "points": points,
            "trend": trend,
        }

    async def compare_runs(self, run_ids: list[str]) -> dict:
        """Side-by-side dimension comparison for completed runs."""
        if not 2 <= len(run_ids) <= 6:
            raise AppError("VALIDATION_ERROR", "Compare 2..6 runs", 422)
        rows = []
        for run_id in run_ids:
            run = await self.get_run(run_id)
            rows.append(
                {
                    "run_id": run.id,
                    "target": run.target,
                    "status": run.status,
                    "dimension_scores": run.dimension_scores or {},
                    "total_cost_usd": float(run.total_cost_usd or 0),
                }
            )
        dims: set[str] = set()
        for row in rows:
            # Only numeric score keys are comparable dimensions; nested
            # structures (dimension_stats) travel with each run untouched
            dims.update(
                k
                for k, v in row["dimension_scores"].items()
                if isinstance(v, (int, float)) or v is None
            )
        return {"runs": rows, "dimensions": sorted(dims)}
