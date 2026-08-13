from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.router import api_v1_router
from app.config import settings
from app.core.database import engine
from app.core.logging import setup_logging
from app.core.redis import redis_pool
from app.exceptions import register_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validate infrastructure connections on startup; warn but don't crash in dev."""
    setup_logging(level=settings.log_level, fmt=settings.log_format)

    log = structlog.get_logger()

    # 1. Verify PostgreSQL
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        log.info("postgres_connected", database=settings.database_url.split("@")[-1])
    except Exception as exc:
        if settings.app_env == "development":
            log.warning("postgres_unavailable", error=str(exc))
        else:
            raise

    # 2. Verify Redis
    try:
        r = redis_pool()
        await r.ping()
        log.info("redis_connected")
    except Exception as exc:
        if settings.app_env == "development":
            log.warning("redis_unavailable", error=str(exc))
        else:
            raise

    # 3. Verify MinIO / S3 bucket (with timeout)
    try:
        import asyncio

        import aioboto3

        async def _check_s3():
            session = aioboto3.Session()
            async with session.client(
                "s3",
                endpoint_url=settings.s3_endpoint,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                region_name=settings.s3_region,
            ) as client:
                try:
                    await client.head_bucket(Bucket=settings.s3_bucket)
                except Exception:
                    await client.create_bucket(Bucket=settings.s3_bucket)
                log.info("s3_bucket_ready", bucket=settings.s3_bucket)

        await asyncio.wait_for(_check_s3(), timeout=5)
    except Exception as exc:
        if settings.app_env == "development":
            log.warning("s3_unavailable", error=str(exc))
        else:
            raise

    log.info("startup_complete", app_env=settings.app_env)

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="OpenSkill Studio API",
    version="0.1.0",
    docs_url="/api/v1/docs" if settings.debug else None,
    redoc_url="/api/v1/redoc" if settings.debug else None,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# ── Middleware stack (registered bottom-up, executed top-down) ──
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

# ── Exception handlers ──
register_exception_handlers(app)

# ── Routes ──
app.include_router(api_v1_router, prefix="/api/v1")
