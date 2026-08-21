from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.rate_limit import rate_limit
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, dependencies=[Depends(rate_limit(60, 60))])
async def liveness():
    """Liveness: is the process alive (no dependency check)."""
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=ReadinessResponse, dependencies=[Depends(rate_limit(10, 60))])
async def readiness(db: AsyncSession = Depends(get_db)):
    """Readiness: can the service accept traffic (checks all dependencies)."""
    components: dict[str, str] = {}

    # PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        components["database"] = "ok"
    except Exception:
        components["database"] = "error"

    # Redis
    try:
        from app.core.redis import redis_pool

        r = redis_pool()
        await r.ping()
        components["redis"] = "ok"
    except Exception:
        components["redis"] = "error"

    all_ok = all(v == "ok" for v in components.values())
    return ReadinessResponse(
        status="ok" if all_ok else "degraded",
        components=components,
    )
