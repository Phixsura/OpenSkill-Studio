"""S3/MinIO object storage abstraction (async)."""

import aioboto3
import structlog

from app.config import settings

log = structlog.get_logger()

_session = aioboto3.Session()


async def get_s3_client():
    """Yield an async S3 client scoped to the current request."""
    async with _session.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    ) as client:
        yield client


async def ensure_bucket(client) -> None:  # noqa: ANN001
    """Create the default bucket if it doesn't exist."""
    try:
        await client.head_bucket(Bucket=settings.s3_bucket)
    except Exception:
        await client.create_bucket(Bucket=settings.s3_bucket)
        log.info("s3_bucket_created", bucket=settings.s3_bucket)
