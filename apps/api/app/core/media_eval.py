"""Media evaluation helpers — S3 image fetch + base64 encoding for LLM vision."""

import base64

import structlog

from app.config import settings
from app.core.storage import get_s3_client
from app.exceptions import AppError

log = structlog.get_logger()

MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20 MB — Anthropic message limit

IMAGE_MIMES = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    }
)


async def fetch_image_as_base64(file_key: str) -> tuple[str, str]:
    """Fetch an image from S3 and return (base64_data, media_type).

    Raises AppError if the file exceeds MAX_IMAGE_SIZE.
    """
    async for client in get_s3_client():
        response = await client.get_object(Bucket=settings.s3_bucket, Key=file_key)
        content_type = response.get("ContentType", "image/png")
        content_length = response.get("ContentLength")

        if content_length is not None and content_length > MAX_IMAGE_SIZE:
            raise AppError(
                "IMAGE_TOO_LARGE",
                f"Image exceeds {MAX_IMAGE_SIZE // (1024 * 1024)}MB limit for evaluation",
                422,
            )

        body = await response["Body"].read()
        # R164: enforce the size cap on the ACTUAL bytes too — a missing/absent
        # ContentLength (defaulted through the check above) or an under-reported
        # one would otherwise let an oversized object through unbounded.
        if len(body) > MAX_IMAGE_SIZE:
            raise AppError(
                "IMAGE_TOO_LARGE",
                f"Image exceeds {MAX_IMAGE_SIZE // (1024 * 1024)}MB limit for evaluation",
                422,
            )
        # R164: validate the S3-reported media type against the set the vision
        # models actually accept. fetch reads ContentType straight from the
        # object (independent of the DB mime the caller gated on) — a stored
        # object whose ContentType is anything else (image/svg+xml, image/bmp,
        # application/octet-stream, or S3's "image/png" default masking non-
        # image bytes) would otherwise be embedded as media_type and make the
        # PAID LLM call reject the ENTIRE multimodal evaluation. Raise instead:
        # the caller wraps this in try/except and degrades to "[Image
        # unavailable]" for the one item, preserving the rest of the eval.
        if content_type not in IMAGE_MIMES:
            raise AppError(
                "IMAGE_MEDIA_TYPE_UNSUPPORTED",
                f"Stored media type '{content_type}' is not an LLM-evaluatable image",
                422,
            )
        b64 = base64.b64encode(body).decode("ascii")
        log.info(
            "image_fetched_for_eval",
            file_key=file_key,
            size_bytes=len(body),
            media_type=content_type,
        )
        return b64, content_type

    raise AppError("S3_ERROR", "Could not fetch image for evaluation", 500)  # pragma: no cover


def build_image_block(base64_data: str, media_type: str) -> dict:
    """Build an Anthropic-style image content block."""
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": base64_data,
        },
    }


def is_image_mime(mime: str | None) -> bool:
    """Check if a MIME type is an evaluatable image."""
    return mime is not None and mime in IMAGE_MIMES


def is_video_mime(mime: str | None) -> bool:
    """Check if a MIME type is a video."""
    return mime is not None and mime.startswith("video/")
