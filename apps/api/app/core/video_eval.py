"""Video frame sampling for multimodal AI evaluation.

Extracts N evenly-spaced frames from a video via ffmpeg subprocess,
encodes them as base64 JPEG images for LLM vision input.

Deterministic sampling: frames at positions duration * i / (N + 1)
for i in 1..N — same video always produces the same frames.
"""

import asyncio
import base64
import json
import os
import shutil
import tempfile

import structlog

from app.config import settings
from app.core.storage import get_s3_client
from app.exceptions import AppError

log = structlog.get_logger()

DEFAULT_MAX_FRAMES = 8
MAX_VIDEO_DURATION_SECONDS = 600  # 10 minutes
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500 MB download cap


def check_ffmpeg() -> None:
    """Pre-flight: verify ffmpeg is installed."""
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise AppError(
            "FFMPEG_NOT_FOUND",
            "ffmpeg/ffprobe not found — required for video evaluation",
            500,
        )


async def _get_video_duration(video_path: str) -> float:
    """Use ffprobe to get video duration in seconds."""
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        video_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    try:
        data = json.loads(stdout)
        return float(data["format"]["duration"])
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        raise AppError("VIDEO_PROBE_FAILED", "Could not determine video duration", 422) from exc


async def _extract_frame(video_path: str, timestamp: float, output_path: str) -> bool:
    """Extract a single frame at the given timestamp."""
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(timestamp),
        "-i",
        video_path,
        "-frames:v",
        "1",
        "-q:v",
        "2",
        output_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    return os.path.exists(output_path) and os.path.getsize(output_path) > 0


async def sample_frames(
    video_path: str,
    num_frames: int = DEFAULT_MAX_FRAMES,
    output_dir: str | None = None,
) -> list[tuple[str, float]]:
    """Extract N evenly-spaced frames from a video.

    Returns list of (frame_path, timestamp_seconds).
    Deterministic: frames at positions duration * i / (num_frames + 1).
    """
    duration = await _get_video_duration(video_path)

    if duration > MAX_VIDEO_DURATION_SECONDS:
        raise AppError(
            "VIDEO_TOO_LONG",
            f"Video exceeds {MAX_VIDEO_DURATION_SECONDS}s limit for evaluation",
            422,
        )

    out_dir = output_dir or tempfile.mkdtemp(prefix="openskill_frames_")
    frames: list[tuple[str, float]] = []

    for i in range(1, num_frames + 1):
        timestamp = duration * i / (num_frames + 1)
        out_path = os.path.join(out_dir, f"frame_{i:03d}.jpg")
        if await _extract_frame(video_path, timestamp, out_path):
            frames.append((out_path, round(timestamp, 2)))

    log.info(
        "video_frames_sampled",
        video_path=video_path,
        duration=duration,
        requested=num_frames,
        extracted=len(frames),
    )
    return frames


def frames_to_base64(frames: list[tuple[str, float]]) -> list[tuple[str, str, float]]:
    """Convert frame files to base64. Returns [(b64, media_type, timestamp)]."""
    result: list[tuple[str, str, float]] = []
    for path, ts in frames:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        result.append((b64, "image/jpeg", ts))
    return result


async def fetch_video_and_sample(
    file_key: str, num_frames: int = DEFAULT_MAX_FRAMES
) -> tuple[list[tuple[str, str, float]], dict]:
    """Full pipeline: S3 download → temp file → ffmpeg sample → base64 → cleanup.

    Returns (frames_data, metadata) where metadata records the sampling strategy
    for storage in EvaluationTask.config.
    """
    check_ffmpeg()

    tmp_dir = tempfile.mkdtemp(prefix="openskill_video_")
    video_path = os.path.join(tmp_dir, "video.mp4")

    try:
        async for client in get_s3_client():
            # Check size before downloading
            head = await client.head_object(Bucket=settings.s3_bucket, Key=file_key)
            size = head.get("ContentLength", 0)
            if size > MAX_VIDEO_SIZE:
                raise AppError(
                    "VIDEO_TOO_LARGE",
                    f"Video exceeds {MAX_VIDEO_SIZE // (1024 * 1024)}MB download limit",
                    422,
                )

            await client.download_file(settings.s3_bucket, file_key, video_path)

        frames = await sample_frames(video_path, num_frames, tmp_dir)
        duration = await _get_video_duration(video_path)
        frames_data = frames_to_base64(frames)

        metadata = {
            "strategy": "uniform",
            "num_frames_requested": num_frames,
            "num_frames_extracted": len(frames_data),
            "video_duration_s": round(duration, 2),
            "frame_timestamps": [ts for _, _, ts in frames_data],
            "video_size_bytes": size,
        }

        return frames_data, metadata
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
