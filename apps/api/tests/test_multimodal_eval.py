"""Tests for multimodal AI evaluation (image/video/prompt/commercial)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.llm import _to_openai_content
from app.core.media_eval import build_image_block, is_image_mime, is_video_mime

# ── LLM client ────────────────────────────────────────────


def test_openai_content_block_translation():
    """Anthropic image blocks are translated to OpenAI image_url format."""
    blocks = [
        {"type": "text", "text": "Evaluate this:"},
        {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": "abc123"},
        },
    ]
    result = _to_openai_content(blocks)
    assert result[0] == {"type": "text", "text": "Evaluate this:"}
    assert result[1]["type"] == "image_url"
    assert result[1]["image_url"]["url"] == "data:image/png;base64,abc123"


def test_openai_unknown_block_passthrough():
    """Unknown block types are passed through as text."""
    blocks = [{"type": "unknown", "data": "stuff"}]
    result = _to_openai_content(blocks)
    assert result[0]["type"] == "text"


# ── Media helpers ─────────────────────────────────────────


def test_build_image_block():
    block = build_image_block("base64data", "image/jpeg")
    assert block["type"] == "image"
    assert block["source"]["type"] == "base64"
    assert block["source"]["media_type"] == "image/jpeg"
    assert block["source"]["data"] == "base64data"


def test_is_image_mime():
    assert is_image_mime("image/png")
    assert is_image_mime("image/jpeg")
    assert not is_image_mime("image/svg+xml")
    assert not is_image_mime("video/mp4")
    assert not is_image_mime(None)


def test_is_video_mime():
    assert is_video_mime("video/mp4")
    assert is_video_mime("video/webm")
    assert not is_video_mime("image/png")
    assert not is_video_mime(None)


# ── Evaluation service multimodal prompt building ─────────


@pytest.mark.asyncio
async def test_image_review_builds_content_blocks():
    """IMAGE_REVIEW eval type produces content blocks with actual image data."""
    from app.services.evaluation import EvaluationService

    db = AsyncMock()
    db.flush = AsyncMock()
    svc = EvaluationService(db)

    # Mock project
    project = MagicMock()
    project.title = "Product Ad"
    project.description = "Create hero image"
    project.rubric = [{"criterion": "Quality", "max_score": 100}]
    project.client_brief_id = None

    # Mock items — one image, one text
    img_item = MagicMock()
    img_item.file_key = "uploads/img.png"
    img_item.mime_type = "image/png"
    img_item.file_name = "img.png"
    img_item.file_size = 5000
    img_item.content = None
    img_item.note = "Hero shot"

    text_item = MagicMock()
    text_item.file_key = None
    text_item.mime_type = None
    text_item.content = "Here is my prompt description"
    text_item.note = None

    task = MagicMock()
    task.type = "image_review"
    task.config = {}

    with patch(
        "app.core.media_eval.fetch_image_as_base64",
        return_value=("b64data", "image/png"),
    ):
        blocks = await svc._build_multimodal_prompt(project, [img_item, text_item], task)

    assert isinstance(blocks, list)
    # Should contain text blocks and at least one image block
    image_blocks = [b for b in blocks if b.get("type") == "image"]
    text_blocks = [b for b in blocks if b.get("type") == "text"]
    assert len(image_blocks) == 1
    assert image_blocks[0]["source"]["data"] == "b64data"
    assert (
        len(text_blocks) >= 3
    )  # context + submission wrapper + note + text content + eval instruction
    # metadata stored
    assert "images_evaluated" in task.config


@pytest.mark.asyncio
async def test_video_review_builds_frame_blocks():
    """VIDEO_REVIEW extracts frames and includes them as image blocks."""
    from app.services.evaluation import EvaluationService

    db = AsyncMock()
    db.flush = AsyncMock()
    svc = EvaluationService(db)

    project = MagicMock()
    project.title = "Video Ad"
    project.description = "Create 15s clip"
    project.rubric = [{"criterion": "Quality", "max_score": 100}]
    project.client_brief_id = None

    video_item = MagicMock()
    video_item.file_key = "uploads/clip.mp4"
    video_item.mime_type = "video/mp4"
    video_item.file_name = "clip.mp4"
    video_item.content = None

    task = MagicMock()
    task.type = "video_review"
    task.config = {}

    mock_frames = [
        ("frame1b64", "image/jpeg", 2.5),
        ("frame2b64", "image/jpeg", 5.0),
        ("frame3b64", "image/jpeg", 7.5),
    ]
    mock_meta = {
        "strategy": "uniform",
        "num_frames_requested": 3,
        "num_frames_extracted": 3,
        "video_duration_s": 10.0,
        "frame_timestamps": [2.5, 5.0, 7.5],
        "video_size_bytes": 1024,
    }

    with patch(
        "app.core.video_eval.fetch_video_and_sample",
        return_value=(mock_frames, mock_meta),
    ):
        blocks = await svc._build_multimodal_prompt(project, [video_item], task)

    image_blocks = [b for b in blocks if b.get("type") == "image"]
    assert len(image_blocks) == 3
    assert "video_sampling" in task.config
    assert task.config["video_sampling"]["num_frames_extracted"] == 3


@pytest.mark.asyncio
async def test_prompt_review_pairs_prompt_and_output():
    """PROMPT_REVIEW includes both the prompt text and the generated output image."""
    from app.models.project import ItemType
    from app.services.evaluation import EvaluationService

    db = AsyncMock()
    db.flush = AsyncMock()
    svc = EvaluationService(db)

    project = MagicMock()
    project.title = "Prompt Craft"
    project.description = "Write effective prompts"
    project.rubric = [{"criterion": "Prompt Quality", "max_score": 50}]
    project.client_brief_id = None

    prompt_item = MagicMock()
    prompt_item.type = ItemType.PROMPT
    prompt_item.content = "A cat wearing a top hat, photorealistic"
    prompt_item.file_key = None
    prompt_item.mime_type = None

    output_item = MagicMock()
    output_item.type = ItemType.FILE
    output_item.content = None
    output_item.file_key = "uploads/cat.png"
    output_item.mime_type = "image/png"
    output_item.file_name = "cat.png"

    task = MagicMock()
    task.type = "prompt_review"
    task.config = {}

    with patch(
        "app.core.media_eval.fetch_image_as_base64",
        return_value=("catb64", "image/png"),
    ):
        blocks = await svc._build_multimodal_prompt(project, [prompt_item, output_item], task)

    text_contents = " ".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    assert "cat wearing a top hat" in text_contents
    image_blocks = [b for b in blocks if b.get("type") == "image"]
    assert len(image_blocks) == 1


@pytest.mark.asyncio
async def test_commercial_review_includes_brief_context():
    """COMMERCIAL_SUBMISSION_REVIEW includes client brief info in the prompt."""
    from app.services.evaluation import EvaluationService

    db = AsyncMock()
    db.flush = AsyncMock()

    brief = MagicMock()
    brief.client_name = "Acme Corp"
    brief.objective = "Product hero shots for Q4 campaign"
    brief.target_audience = "Young professionals"
    brief.tone_and_style = "Modern, clean, minimalist"
    brief.constraints = "Must include product logo"
    brief.evaluation_criteria = [{"criterion": "Brand alignment", "weight": 0.3}]

    db.get = AsyncMock(return_value=brief)
    svc = EvaluationService(db)

    project = MagicMock()
    project.title = "Acme Q4"
    project.description = "Commercial work"
    project.rubric = [{"criterion": "Quality", "max_score": 100}]
    project.client_brief_id = "brief123"

    img_item = MagicMock()
    img_item.file_key = "uploads/hero.jpg"
    img_item.mime_type = "image/jpeg"
    img_item.file_name = "hero.jpg"
    img_item.file_size = 2000
    img_item.content = None
    img_item.note = None

    task = MagicMock()
    task.type = "commercial_submission_review"
    task.config = {}

    with patch(
        "app.core.media_eval.fetch_image_as_base64",
        return_value=("herob64", "image/jpeg"),
    ):
        blocks = await svc._build_multimodal_prompt(project, [img_item], task)

    text = " ".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    assert "Acme Corp" in text
    assert "Product hero shots" in text
    assert "Young professionals" in text
    assert "minimalist" in text


@pytest.mark.asyncio
async def test_text_eval_unchanged():
    """Existing SUBMISSION_REVIEW type still uses the text-only path."""
    from app.services.evaluation import _MULTIMODAL_EVAL_TYPES

    assert "submission_review" not in {t.value for t in _MULTIMODAL_EVAL_TYPES}


@pytest.mark.asyncio
async def test_image_fetch_failure_graceful():
    """If image fetch fails, a placeholder text block is used, not a crash."""
    from app.services.evaluation import EvaluationService

    db = AsyncMock()
    db.flush = AsyncMock()
    svc = EvaluationService(db)

    project = MagicMock()
    project.title = "Fail Test"
    project.description = "d"
    project.rubric = [{"criterion": "Q", "max_score": 100}]
    project.client_brief_id = None

    img_item = MagicMock()
    img_item.file_key = "uploads/missing.png"
    img_item.mime_type = "image/png"
    img_item.file_name = "missing.png"
    img_item.file_size = 1000
    img_item.content = None
    img_item.note = None

    task = MagicMock()
    task.type = "image_review"
    task.config = {}

    with patch(
        "app.core.media_eval.fetch_image_as_base64",
        side_effect=Exception("S3 down"),
    ):
        blocks = await svc._build_multimodal_prompt(project, [img_item], task)

    text = " ".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    assert "Image unavailable" in text
    # No image blocks
    assert not any(b.get("type") == "image" for b in blocks)


@pytest.mark.asyncio
async def test_eval_type_routes_correctly():
    """Each multimodal eval type routes to the correct system prompt."""
    from app.models.evaluation import EvalType
    from app.services.evaluation import (
        _MULTIMODAL_SYSTEM_PROMPTS,
        COMMERCIAL_REVIEW_SYSTEM_PROMPT,
        IMAGE_REVIEW_SYSTEM_PROMPT,
        PROMPT_REVIEW_SYSTEM_PROMPT,
        VIDEO_REVIEW_SYSTEM_PROMPT,
    )

    assert _MULTIMODAL_SYSTEM_PROMPTS[EvalType.IMAGE_REVIEW] is IMAGE_REVIEW_SYSTEM_PROMPT
    assert _MULTIMODAL_SYSTEM_PROMPTS[EvalType.VIDEO_REVIEW] is VIDEO_REVIEW_SYSTEM_PROMPT
    assert _MULTIMODAL_SYSTEM_PROMPTS[EvalType.PROMPT_REVIEW] is PROMPT_REVIEW_SYSTEM_PROMPT
    assert (
        _MULTIMODAL_SYSTEM_PROMPTS[EvalType.COMMERCIAL_SUBMISSION_REVIEW]
        is COMMERCIAL_REVIEW_SYSTEM_PROMPT
    )


# ── Video eval unit tests ────────────────────────────────


def test_video_eval_check_ffmpeg():
    """check_ffmpeg doesn't raise when ffmpeg is installed."""
    from app.core.video_eval import check_ffmpeg

    # Should not raise on CI/local where ffmpeg is installed
    check_ffmpeg()


# ── Integration: new eval types accepted ─────────────────


@pytest.mark.asyncio
async def test_new_eval_types_accepted_by_schema():
    """TriggerEvaluationRequest accepts the new multimodal eval types."""
    from app.schemas.evaluation import TriggerEvaluationRequest

    for t in ("image_review", "video_review", "prompt_review", "commercial_submission_review"):
        req = TriggerEvaluationRequest(submission_id="test123", type=t)
        assert req.type == t


@pytest.mark.asyncio
async def test_invalid_eval_type_still_rejected():
    """Bogus eval types are still rejected by schema validation."""
    from pydantic import ValidationError

    from app.schemas.evaluation import TriggerEvaluationRequest

    with pytest.raises(ValidationError):
        TriggerEvaluationRequest(submission_id="test123", type="bogus_type")
