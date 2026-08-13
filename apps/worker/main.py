"""ARQ worker for async evaluation tasks.

Phase 1: Not required — evaluations run inline in the API process.
Phase 2+: Run from the apps/api directory:
    cd apps/api && uv run arq apps.worker.main.WorkerSettings

Or with PYTHONPATH if running from project root:
    PYTHONPATH=apps/api arq apps.worker.main.WorkerSettings
"""

from arq.connections import RedisSettings

from app.config import settings


async def startup(ctx: dict) -> None:
    """Initialize DB engine + LLM client on worker startup."""
    from app.core.database import engine
    from app.core.llm import create_llm_client
    from app.core.logging import setup_logging

    setup_logging(level=settings.log_level, fmt=settings.log_format)
    ctx["db_engine"] = engine
    ctx["llm"] = create_llm_client()


async def shutdown(ctx: dict) -> None:
    """Dispose DB engine on shutdown."""
    await ctx["db_engine"].dispose()


async def evaluate_submission(ctx: dict, task_id: str) -> None:
    """ARQ task: evaluate a project submission."""
    from app.core.database import AsyncSessionLocal
    from app.models.evaluation import EvaluationTask
    from app.services.evaluation import EvaluationService

    async with AsyncSessionLocal() as db:
        task = await db.get(EvaluationTask, task_id)
        if task is None:
            return

        svc = EvaluationService(db)
        await svc._execute_evaluation(task)
        await db.commit()


async def evaluate_exercise(ctx: dict, task_id: str) -> None:
    """ARQ task: evaluate an exercise attempt."""
    # Phase 2+: implement exercise-specific evaluation
    await evaluate_submission(ctx, task_id)


class WorkerSettings:
    """ARQ worker configuration."""

    functions = [evaluate_submission, evaluate_exercise]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = settings.eval_max_concurrent
    job_timeout = settings.eval_timeout_seconds
    max_tries = settings.eval_max_retries
    retry_defer = 30
    queue_name = "openskill:eval"
