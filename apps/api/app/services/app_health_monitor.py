"""App health monitoring — periodic health checks and alerting.

Provides health scoring, threshold-based alerting, and status tracking
for installed apps.
"""

from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.developer import (
    AppInstallation,
    SandboxExecution,
    SandboxExecutionStatus,
)

log = structlog.get_logger()


class HealthScore:
    """Compute a 0-100 health score for an app."""

    def __init__(self, total_executions: int, failed_executions: int, timeout_executions: int):
        self.total = total_executions
        self.failed = failed_executions
        self.timeout = timeout_executions

    @property
    def score(self) -> int:
        if self.total == 0:
            return 100  # No data = healthy by default
        error_rate = (self.failed + self.timeout) / self.total
        return max(0, int((1 - error_rate) * 100))

    @property
    def status(self) -> str:
        s = self.score
        if s >= 95:
            return "healthy"
        if s >= 80:
            return "degraded"
        if s >= 50:
            return "warning"
        return "critical"

    @property
    def error_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.failed + self.timeout) / self.total * 100, 1)

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "status": self.status,
            "error_rate_pct": self.error_rate,
            "total_executions": self.total,
            "failed_executions": self.failed,
            "timeout_executions": self.timeout,
        }


async def compute_health_score(
    db: AsyncSession, app_id: str, *, hours: int = 24
) -> HealthScore:
    """Compute health score for an app over the last N hours."""
    since = datetime.now(UTC) - timedelta(hours=hours)

    result = await db.execute(
        select(
            func.count().label("total"),
            func.count()
            .filter(SandboxExecution.status == SandboxExecutionStatus.FAILED)
            .label("failed"),
            func.count()
            .filter(SandboxExecution.status == SandboxExecutionStatus.TIMEOUT)
            .label("timeout"),
        )
        .select_from(SandboxExecution)
        .join(AppInstallation, SandboxExecution.installation_id == AppInstallation.id)
        .where(
            AppInstallation.app_id == app_id,
            SandboxExecution.created_at >= since,
        )
    )
    row = result.one()
    return HealthScore(
        total_executions=row.total or 0,
        failed_executions=row.failed or 0,
        timeout_executions=row.timeout or 0,
    )
