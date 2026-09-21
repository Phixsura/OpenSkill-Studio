"""Blind A/B human benchmark review (ADR-016 §3.6).

Model/provider identity is hidden behind alias labels ("Model A") until every
reviewer in the batch has submitted AND an admin reveals. The alias_map lives
server-side only; reviewer-facing payloads never contain the run target.
"""

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.benchmark import (
    BenchmarkResult,
    BenchmarkReview,
    BenchmarkRun,
    ReviewBatch,
)
from app.exceptions import AppError

_ALIAS_LABELS = [f"Model {c}" for c in "ABCDEFGH"]


class BlindReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_batch(
        self,
        *,
        suite_id: str,
        run_ids: list[str],
        reviewer_ids: list[str],
        blind: bool = True,
        created_by: str | None = None,
    ) -> ReviewBatch:
        if not 2 <= len(run_ids) <= len(_ALIAS_LABELS):
            raise AppError("VALIDATION_ERROR", f"Batch needs 2..{len(_ALIAS_LABELS)} runs", 422)
        if not reviewer_ids:
            raise AppError("VALIDATION_ERROR", "Batch needs at least one reviewer", 422)
        runs: list[BenchmarkRun] = []
        for run_id in run_ids:
            run = await self.db.get(BenchmarkRun, run_id)
            if not run or run.suite_id != suite_id:
                raise AppError("NOT_FOUND", "Run not found in suite", 404)
            if run.status != "completed":
                raise AppError("VALIDATION_ERROR", "Only completed runs can be reviewed", 422)
            runs.append(run)
        # Random alias permutation — reviewer order carries no identity signal
        labels = _ALIAS_LABELS[: len(run_ids)]
        shuffled = list(labels)
        for i in range(len(shuffled) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        alias_map = {run.id: shuffled[i] for i, run in enumerate(runs)}

        batch = ReviewBatch(
            suite_id=suite_id,
            run_ids=run_ids,
            alias_map=alias_map,
            reviewer_ids=reviewer_ids,
            blind=blind,
            created_by=created_by,
        )
        self.db.add(batch)
        await self.db.flush()

        # Pre-create one review row per (result, reviewer)
        for run in runs:
            results = await self.db.scalars(
                select(BenchmarkResult).where(BenchmarkResult.run_id == run.id)
            )
            for result in results:
                for reviewer_id in reviewer_ids:
                    self.db.add(
                        BenchmarkReview(
                            batch_id=batch.id,
                            run_id=run.id,
                            result_id=result.id,
                            reviewer_id=reviewer_id,
                            alias_label=alias_map[run.id],
                        )
                    )
        await self.db.flush()
        return batch

    async def get_batch(self, batch_id: str) -> ReviewBatch:
        batch = await self.db.get(ReviewBatch, batch_id)
        if not batch:
            raise AppError("NOT_FOUND", "Review batch not found", 404)
        return batch

    async def assignments_for(self, batch_id: str, reviewer_id: str) -> list[dict]:
        """Reviewer-facing assignments — identity is the alias label ONLY."""
        batch = await self.get_batch(batch_id)
        if reviewer_id not in (batch.reviewer_ids or []):
            raise AppError("NOT_FOUND", "Review batch not found", 404)  # no oracle
        reviews = await self.db.scalars(
            select(BenchmarkReview).where(
                BenchmarkReview.batch_id == batch_id,
                BenchmarkReview.reviewer_id == reviewer_id,
            )
        )
        out = []
        for review in reviews:
            result = await self.db.get(BenchmarkResult, review.result_id)
            out.append(
                {
                    "review_id": review.id,
                    "alias_label": review.alias_label,
                    "output_assets": result.output_assets if result else [],
                    "input_snapshot": (result.input_snapshot or {}) if result else {},
                    "submitted": review.submitted_at is not None,
                    "scores": review.scores or {},
                    # Deliberately ABSENT: run_id/target/provider/model identity
                }
            )
        return out

    async def submit(
        self, review_id: str, *, reviewer_id: str, scores: dict, comment: str | None = None
    ) -> BenchmarkReview:
        review = await self.db.get(BenchmarkReview, review_id)
        if not review or review.reviewer_id != reviewer_id:
            raise AppError("NOT_FOUND", "Review not found", 404)
        if review.submitted_at is not None:
            raise AppError("ECO_INVALID_TRANSITION", "Review already submitted", 409)
        clean_scores = {}
        for dim, value in (scores or {}).items():
            if not isinstance(dim, str):
                continue
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue
            if numeric != numeric or not 0 <= numeric <= 5:
                raise AppError("VALIDATION_ERROR", f"Score {dim} out of 0..5", 422)
            clean_scores[dim[:60]] = numeric
        if not clean_scores:
            raise AppError("VALIDATION_ERROR", "At least one dimension score required", 422)
        review.scores = clean_scores
        review.comment = comment
        review.submitted_at = datetime.now(UTC)
        await self.db.flush()
        await self._maybe_complete(review.batch_id)
        return review

    async def _maybe_complete(self, batch_id: str) -> None:
        pending = await self.db.scalar(
            select(BenchmarkReview.id)
            .where(
                BenchmarkReview.batch_id == batch_id,
                BenchmarkReview.submitted_at.is_(None),
            )
            .limit(1)
        )
        if pending is None:
            batch = await self.db.get(ReviewBatch, batch_id)
            if batch and batch.status == "open":
                batch.status = "complete"
                await self.db.flush()

    async def _bradley_terry_elo(self, batch: ReviewBatch) -> dict[str, float]:
        """LMArena-method Elo: each reviewer's scores on the same case form
        pairwise preferences between runs; Bradley-Terry MLE turns those into
        a preference rating. Ties count half. Uses the mean of each review's
        dimension scores as the reviewer's overall preference signal."""
        from app.ecosystem.services.stats import bradley_terry, pairwise_wins_from_scores

        reviews = await self.db.scalars(
            select(BenchmarkReview).where(
                BenchmarkReview.batch_id == batch.id,
                BenchmarkReview.submitted_at.isnot(None),
            )
        )
        reviews = list(reviews)
        if not reviews:
            return {}
        result_case: dict[str, str] = {}
        for review in reviews:
            if review.result_id not in result_case:
                result = await self.db.get(BenchmarkResult, review.result_id)
                result_case[review.result_id] = result.case_id if result else review.result_id
        rows = []
        for review in reviews:
            scores = [v for v in (review.scores or {}).values() if isinstance(v, (int, float))]
            if not scores:
                continue
            rows.append(
                {
                    "context": result_case.get(review.result_id, review.result_id),
                    "judge": review.reviewer_id,
                    "item": review.run_id,
                    "score": sum(scores) / len(scores),
                }
            )
        return bradley_terry(pairwise_wins_from_scores(rows))

    async def reveal(self, batch_id: str) -> dict:
        """Reveal identities — refused until every review is submitted."""
        batch = await self.get_batch(batch_id)
        if batch.status == "open":
            raise AppError(
                "ECO_BLIND_REVIEW_SEALED",
                "Identities stay hidden until all reviewers submit",
                409,
            )
        batch.status = "revealed"
        await self.db.flush()
        # Fold human dimensions back into each run's preserved scores +
        # Bradley-Terry preference Elo from the blind pairwise structure
        from app.ecosystem.services.benchmark import BenchmarkService

        elo = await self._bradley_terry_elo(batch)
        bench = BenchmarkService(self.db)
        revealed = []
        for run_id in batch.run_ids or []:
            run = await bench.refresh_dimensions(run_id)
            if run_id in elo:
                scores = dict(run.dimension_scores or {})
                scores["human_pref_elo"] = elo[run_id]
                run.dimension_scores = scores
                await self.db.flush()
            revealed.append(
                {
                    "run_id": run_id,
                    "alias_label": (batch.alias_map or {}).get(run_id),
                    "target": run.target,
                    "dimension_scores": run.dimension_scores,
                }
            )
        return {"batch_id": batch.id, "runs": revealed}
