"""Coverage tests for media_eval.py and video_eval.py.

Uses mocks for S3 and ffmpeg to test all code paths.
"""

import base64
import os
import tempfile
from unittest.mock import AsyncMock, patch

import pytest

from app.core.media_eval import (
    IMAGE_MIMES,
    MAX_IMAGE_SIZE,
    build_image_block,
    is_image_mime,
    is_video_mime,
)

# ═══════════════ media_eval.py ═══════════════


def test_build_image_block_structure():
    block = build_image_block("abc123", "image/jpeg")
    assert block == {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "abc123",
        },
    }


def test_is_image_mime_valid():
    assert is_image_mime("image/png") is True
    assert is_image_mime("image/jpeg") is True
    assert is_image_mime("image/gif") is True
    assert is_image_mime("image/webp") is True


def test_is_image_mime_invalid():
    assert is_image_mime("video/mp4") is False
    assert is_image_mime("text/plain") is False
    assert is_image_mime(None) is False
    assert is_image_mime("") is False


def test_is_video_mime():
    assert is_video_mime("video/mp4") is True
    assert is_video_mime("video/webm") is True
    assert is_video_mime("video/quicktime") is True
    assert is_video_mime("image/png") is False
    assert is_video_mime(None) is False


def test_image_mimes_completeness():
    assert len(IMAGE_MIMES) == 4
    assert all(m.startswith("image/") for m in IMAGE_MIMES)


def test_max_image_size():
    assert MAX_IMAGE_SIZE == 20 * 1024 * 1024


@pytest.mark.asyncio
async def test_fetch_image_as_base64_success():
    """Mock S3 to test successful image fetch."""
    from app.core.media_eval import fetch_image_as_base64

    fake_body = b"fake image data"

    # Mock the S3 client
    mock_body = AsyncMock()
    mock_body.read = AsyncMock(return_value=fake_body)

    mock_response = {
        "ContentType": "image/png",
        "ContentLength": len(fake_body),
        "Body": mock_body,
    }

    mock_client = AsyncMock()
    mock_client.get_object = AsyncMock(return_value=mock_response)

    async def fake_get_s3():
        yield mock_client

    with patch("app.core.media_eval.get_s3_client", fake_get_s3):
        b64, media_type = await fetch_image_as_base64("test/image.png")

    assert media_type == "image/png"
    assert b64 == base64.b64encode(fake_body).decode("ascii")


@pytest.mark.asyncio
async def test_fetch_image_as_base64_too_large():
    """Image exceeding size limit raises AppError."""
    from app.core.media_eval import fetch_image_as_base64
    from app.exceptions import AppError

    mock_response = {
        "ContentType": "image/png",
        "ContentLength": 25 * 1024 * 1024,  # 25MB > 20MB limit
        "Body": AsyncMock(),
    }
    mock_client = AsyncMock()
    mock_client.get_object = AsyncMock(return_value=mock_response)

    async def fake_get_s3():
        yield mock_client

    with patch("app.core.media_eval.get_s3_client", fake_get_s3):
        with pytest.raises(AppError) as exc_info:
            await fetch_image_as_base64("test/large.png")
        assert exc_info.value.code == "IMAGE_TOO_LARGE"


# ═══════════════ video_eval.py ═══════════════


def test_check_ffmpeg_available():
    """check_ffmpeg doesn't raise when ffmpeg is installed."""
    from app.core.video_eval import check_ffmpeg

    if os.popen("which ffmpeg").read().strip():
        check_ffmpeg()  # Should not raise
    else:
        from app.exceptions import AppError

        with pytest.raises(AppError):
            check_ffmpeg()


def test_check_ffmpeg_missing():
    """check_ffmpeg raises when ffmpeg not found."""
    from app.core.video_eval import check_ffmpeg
    from app.exceptions import AppError

    with patch("app.core.video_eval.shutil.which", return_value=None):
        with pytest.raises(AppError) as exc_info:
            check_ffmpeg()
        assert exc_info.value.code == "FFMPEG_NOT_FOUND"


def test_frames_to_base64_empty():
    """Empty frame list returns empty result."""
    from app.core.video_eval import frames_to_base64

    result = frames_to_base64([])
    assert result == []


def test_frames_to_base64_with_file():
    """Converts a real file to base64."""
    from app.core.video_eval import frames_to_base64

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"\xff\xd8\xff\xe0" + b"\x00" * 100)  # Fake JPEG header
        path = f.name

    try:
        result = frames_to_base64([(path, 2.5)])
        assert len(result) == 1
        b64, media_type, ts = result[0]
        assert media_type == "image/jpeg"
        assert ts == 2.5
        assert len(b64) > 0
        # Verify it's valid base64
        decoded = base64.b64decode(b64)
        assert decoded[:4] == b"\xff\xd8\xff\xe0"
    finally:
        os.unlink(path)


@pytest.mark.asyncio
async def test_get_video_duration_success():
    """Mock ffprobe to return a duration."""
    from app.core.video_eval import _get_video_duration

    fake_output = b'{"format": {"duration": "42.5"}}'

    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(fake_output, b""))

    with patch("app.core.video_eval.asyncio.create_subprocess_exec", return_value=mock_proc):
        duration = await _get_video_duration("/fake/video.mp4")

    assert duration == 42.5


@pytest.mark.asyncio
async def test_get_video_duration_parse_error():
    """Invalid ffprobe output raises AppError."""
    from app.core.video_eval import _get_video_duration
    from app.exceptions import AppError

    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(b"not json", b""))

    with patch("app.core.video_eval.asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(AppError) as exc_info:
            await _get_video_duration("/fake/video.mp4")
        assert exc_info.value.code == "VIDEO_PROBE_FAILED"


@pytest.mark.asyncio
async def test_extract_frame_success():
    """Mock ffmpeg frame extraction."""
    from app.core.video_eval import _extract_frame

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"fake frame data")
        output_path = f.name

    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(b"", b""))

    with patch("app.core.video_eval.asyncio.create_subprocess_exec", return_value=mock_proc):
        result = await _extract_frame("/fake/video.mp4", 5.0, output_path)

    assert result is True
    os.unlink(output_path)


@pytest.mark.asyncio
async def test_sample_frames_too_long():
    """Video exceeding duration limit raises AppError."""
    from app.core.video_eval import sample_frames
    from app.exceptions import AppError

    with patch("app.core.video_eval._get_video_duration", return_value=700.0):
        with pytest.raises(AppError) as exc_info:
            await sample_frames("/fake/video.mp4")
        assert exc_info.value.code == "VIDEO_TOO_LONG"


@pytest.mark.asyncio
async def test_fetch_video_and_sample_too_large():
    """Video exceeding size limit raises AppError."""
    from app.core.video_eval import fetch_video_and_sample
    from app.exceptions import AppError

    mock_client = AsyncMock()
    mock_client.head_object = AsyncMock(
        return_value={"ContentLength": 600 * 1024 * 1024}  # 600MB > 500MB
    )

    async def fake_get_s3():
        yield mock_client

    with (
        patch("app.core.video_eval.get_s3_client", fake_get_s3),
        patch("app.core.video_eval.check_ffmpeg"),
    ):
        with pytest.raises(AppError) as exc_info:
            await fetch_video_and_sample("test/video.mp4")
        assert exc_info.value.code == "VIDEO_TOO_LARGE"
