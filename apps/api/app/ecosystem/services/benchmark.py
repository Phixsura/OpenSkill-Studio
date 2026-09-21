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
        self.executor = executor or MockExecutor()

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
        run = BenchmarkRun(
            suite_id=suite_id,
            target=target,
            budget_usd_cap=budget_usd_cap or suite.budget_usd_cap,
            seed_settings=seed_settings or {},
            environment_snapshot={"executor": type(self.executor).__name__, "suite_key": suite.key},
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
        suite = await self.get_suite(run.suite_id)
        cases = await self.list_cases(run.suite_id)
        if not cases:
            run.status = "failed"
            run.error = "Suite has no cases"
            await self.db.flush()
            return run
        run.status = "running"
        run.started_at = datetime.now(UTC)
        await self.db.flush()

        total_cost = Decimal("0")
        budget = Decimal(str(run.budget_usd_cap))
        aborted = False
        for case in cases:
            for repeat in range(suite.repeat_count):
                if total_cost >= budget:
                    aborted = True
                    break
                try:
                    outcome = await self.executor.execute_case(run, case, repeat)
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
        return run

    async def _aggregate(self, run: BenchmarkRun) -> dict:
        """Aggregate results into preserved per-dimension scores."""
        results = await self.db.scalars(
            select(BenchmarkResult).where(BenchmarkResult.run_id == run.id)
        )
        results = list(results)
        if not results:
            return {}
        latencies = [r.latency_ms for r in results if r.latency_ms is not None]
        costs = [float(r.cost_usd or 0) for r in results]
        failures = sum(1 for r in results if r.failed)
        dims: dict = {
            "reliability": round(1 - failures / len(results), 4),
            "speed_p50_ms": statistics.median(latencies) if latencies else None,
            "cost_per_case_usd": round(sum(costs) / len(results), 6),
        }
        # Automated metric means become their own dimensions
        metric_values: dict[str, list[float]] = {}
        for r in results:
            for key, value in (r.automated_scores or {}).items():
                if isinstance(value, (int, float)) and value == value:
                    metric_values.setdefault(key, []).append(float(value))
        for key, values in metric_values.items():
            dims[key] = round(sum(values) / len(values), 4)
        # Human-review dimensions merge in after blind reveal (see blind_review)
        human = await self._human_dimensions(run.id)
        dims.update(human)
        return dims

    async def _human_dimensions(self, run_id: str) -> dict:
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
        return {dim: round(sum(v) / len(v), 4) for dim, v in buckets.items()}

    async def refresh_dimensions(self, run_id: str) -> BenchmarkRun:
        """Re-aggregate after human reviews land (post-reveal)."""
        run = await self.db.get(BenchmarkRun, run_id)
        if not run:
            raise AppError("NOT_FOUND", "Run not found", 404)
        run.dimension_scores = await self._aggregate(run)
        await self.db.flush()
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
            dims.update(row["dimension_scores"].keys())
        return {"runs": rows, "dimensions": sorted(dims)}
