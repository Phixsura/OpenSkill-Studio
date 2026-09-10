"""S3/MinIO object storage abstraction (async)."""

import aioboto3
import structlog
from botocore.config import Config as _BotoConfig

from app.config import settings

log = structlog.get_logger()

_session = aioboto3.Session()

# R201 (chaos probe: docker-paused MinIO): with no botocore timeouts an S3
# outage HUNG every S3-touching request >90s (60s connect + retries) — the
# same soft-outage class as R196's Redis timeouts. Tight connect, generous
# read (large media uploads/downloads read in chunks), two attempts total.
# NOTE: a docker-pause outage looks like connect-success + silent socket
# (the port proxy accepts), so READ timeout — not connect — bounds the hang,
# and botocore retries multiply it. One attempt, 10s: an outage costs a
# request ≤10s and the user/outbox retries; healthy local S3 answers in ms.
_S3_CONFIG = _BotoConfig(
    connect_timeout=2,
    read_timeout=10,
    retries={"max_attempts": 1, "mode": "standard"},
)


async def get_s3_client():
    """Yield an async S3 client scoped to the current request."""
    async with _session.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=_S3_CONFIG,
    ) as client:
        yield client


async def ensure_bucket(client) -> None:  # noqa: ANN001
    """Create the default bucket if it doesn't exist."""
    from botocore.exceptions import ClientError

    try:
        await client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchBucket"):
            await client.create_bucket(Bucket=settings.s3_bucket)
            log.info("s3_bucket_created", bucket=settings.s3_bucket)
        else:
            raise
