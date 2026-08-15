"""Template, asset, and prompt endpoint tests (no DB — auth/validation/unit)."""

import pytest

from app.models.project import DeliverableType, ItemType
from app.services.project import BUILTIN_TEMPLATES, MEDIA_MIME_WHITELIST, PROJECT_TYPES

ORG = "01JGJ0000000000000000000AA"
PROJECT = "01JGJ0000000000000000000BB"
SUB = "01JGJ0000000000000000000CC"


# ── Enum coverage ──


def test_new_deliverable_types_exist():
    values = {t.value for t in DeliverableType}
    for expected in ("image", "video", "audio", "prompt", "reference", "final_output"):
        assert expected in values
    # Originals intact
    for legacy in ("file", "text", "link", "markdown"):
        assert legacy in values


def test_prompt_item_type_exists():
    assert ItemType.PROMPT.value == "prompt"


def test_project_types():
    assert {"general", "ai_visual"} == PROJECT_TYPES


def test_media_whitelist_covers_media_types():
    assert DeliverableType.IMAGE in MEDIA_MIME_WHITELIST
    assert DeliverableType.VIDEO in MEDIA_MIME_WHITELIST
    assert DeliverableType.AUDIO in MEDIA_MIME_WHITELIST
    assert DeliverableType.REFERENCE in MEDIA_MIME_WHITELIST
    assert DeliverableType.FINAL_OUTPUT in MEDIA_MIME_WHITELIST
    # FILE stays unrestricted
    assert DeliverableType.FILE not in MEDIA_MIME_WHITELIST


# ── Builtin template shape ──


def test_builtin_template_exists():
    assert len(BUILTIN_TEMPLATES) >= 1
    t = BUILTIN_TEMPLATES[0]
    assert t["id"] == "builtin-ai-product-ad"
    assert t["name"] == "AI Product Advertisement"
    assert t["project_type"] == "ai_visual"


def test_builtin_template_has_8_stages():
    t = BUILTIN_TEMPLATES[0]
    assert len(t["deliverables"]) == 8
    names = [d["name"] for d in t["deliverables"]]
    assert names == [
        "Client Brief",
        "Creative Concept",
        "Reference Assets",
        "Prompt Design",
        "Key Visuals",
        "Storyboard",
        "Video Clips",
        "Final Video",
    ]


def test_builtin_template_deliverable_types_valid():
    valid = {t.value for t in DeliverableType}
    for d in BUILTIN_TEMPLATES[0]["deliverables"]:
        assert d["type"] in valid, f"invalid type {d['type']}"


def test_builtin_template_stage_order_sequential():
    orders = [d["sort_order"] for d in BUILTIN_TEMPLATES[0]["deliverables"]]
    assert orders == sorted(orders) == list(range(8))


def test_builtin_template_rubric_sums_to_max_score():
    t = BUILTIN_TEMPLATES[0]
    assert sum(r["max_score"] for r in t["rubric"]) == t["max_score"]


def test_builtin_template_media_configs_are_safe():
    """accepted_formats must be within the type whitelist; sizes within global cap."""
    t = BUILTIN_TEMPLATES[0]
    for d in t["deliverables"]:
        cfg = d.get("config", {})
        max_mb = cfg.get("max_file_size_mb")
        if max_mb is not None:
            assert max_mb <= 50
        accepted = cfg.get("accepted_formats")
        if accepted:
            dtype = DeliverableType(d["type"])
            whitelist = MEDIA_MIME_WHITELIST[dtype]
            for mime in accepted:
                assert mime in whitelist, f"{mime} not in whitelist for {dtype}"


# ── Auth: all new routes reject unauthenticated ──


@pytest.mark.asyncio
async def test_templates_list_requires_auth(client):
    r = await client.get(f"/api/v1/orgs/{ORG}/project-templates")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_templates_create_requires_auth(client):
    r = await client.post(f"/api/v1/orgs/{ORG}/project-templates", json={})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_template_get_requires_auth(client):
    r = await client.get(f"/api/v1/orgs/{ORG}/project-templates/builtin-ai-product-ad")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_from_template_requires_auth(client):
    r = await client.post(
        f"/api/v1/orgs/{ORG}/projects/from-template",
        json={"template_id": "builtin-ai-product-ad"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_assets_list_requires_auth(client):
    r = await client.get(f"/api/v1/orgs/{ORG}/projects/{PROJECT}/assets")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_asset_download_requires_auth(client):
    r = await client.get(f"/api/v1/orgs/{ORG}/projects/{PROJECT}/assets/XYZ/download")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_prompt_item_requires_auth(client):
    r = await client.post(
        f"/api/v1/orgs/{ORG}/submissions/{SUB}/prompt-items",
        json={"deliverable_id": "X", "prompt": "test"},
    )
    assert r.status_code == 401


# ── Schema validation (401 or 422 acceptable without auth; use model directly) ──


def test_create_project_invalid_project_type():
    from pydantic import ValidationError

    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError):
        CreateProjectRequest(
            title="Test",
            description="d",
            instructions="i",
            project_type="quantum",
            rubric=[{"criterion": "Q", "max_score": 100}],
        )


def test_create_project_valid_ai_visual():
    from app.schemas.project import CreateProjectRequest

    req = CreateProjectRequest(
        title="Test",
        description="d",
        instructions="i",
        project_type="ai_visual",
        rubric=[{"criterion": "Q", "max_score": 100}],
    )
    assert req.project_type == "ai_visual"


def test_template_request_invalid_deliverable_type():
    from pydantic import ValidationError

    from app.schemas.project import CreateTemplateRequest

    with pytest.raises(ValidationError):
        CreateTemplateRequest(
            name="T",
            description="d",
            instructions="i",
            rubric=[{"criterion": "Q", "max_score": 100}],
            deliverables=[{"name": "Bad", "type": "hologram"}],
        )


def test_template_request_deliverable_name_too_short():
    from pydantic import ValidationError

    from app.schemas.project import CreateTemplateRequest

    with pytest.raises(ValidationError):
        CreateTemplateRequest(
            name="T",
            description="d",
            instructions="i",
            rubric=[{"criterion": "Q", "max_score": 100}],
            deliverables=[{"name": "X", "type": "image"}],
        )


def test_template_request_too_many_deliverables():
    from pydantic import ValidationError

    from app.schemas.project import CreateTemplateRequest

    with pytest.raises(ValidationError):
        CreateTemplateRequest(
            name="T",
            description="d",
            instructions="i",
            rubric=[{"criterion": "Q", "max_score": 100}],
            deliverables=[{"name": f"D{i:02d}", "type": "text"} for i in range(31)],
        )


def test_template_request_valid():
    from app.schemas.project import CreateTemplateRequest

    req = CreateTemplateRequest(
        name="My Template",
        description="d",
        instructions="i",
        project_type="ai_visual",
        rubric=[{"criterion": "Q", "max_score": 100}],
        deliverables=[
            {"name": "Hero Image", "type": "image", "required": True, "config": {}},
        ],
    )
    assert req.deliverables[0]["type"] == "image"


def test_template_request_bad_rubric_keys_rejected():
    """A template rubric is copied verbatim into a project, so it must satisfy
    the same per-item constraints (criterion + max_score keys)."""
    from pydantic import ValidationError

    from app.schemas.project import CreateTemplateRequest

    with pytest.raises(ValidationError):
        CreateTemplateRequest(
            name="Bad Rubric Template",
            description="d",
            instructions="i",
            rubric=[{"wrong": "keys"}],
            deliverables=[],
        )


def test_template_request_negative_rubric_score_rejected():
    from pydantic import ValidationError

    from app.schemas.project import CreateTemplateRequest

    with pytest.raises(ValidationError):
        CreateTemplateRequest(
            name="Neg Rubric Template",
            description="d",
            instructions="i",
            rubric=[{"criterion": "Q", "max_score": -5}],
            deliverables=[],
        )


def test_prompt_request_empty_prompt_rejected():
    from pydantic import ValidationError

    from app.schemas.project import PromptItemRequest

    with pytest.raises(ValidationError):
        PromptItemRequest(deliverable_id="X", prompt="   ")


def test_prompt_request_too_long_rejected():
    from pydantic import ValidationError

    from app.schemas.project import PromptItemRequest

    with pytest.raises(ValidationError):
        PromptItemRequest(deliverable_id="X", prompt="p" * 10001)


def test_prompt_request_valid():
    from app.schemas.project import PromptItemRequest

    req = PromptItemRequest(
        deliverable_id="X",
        prompt="Create a cinematic product shot of a watch on marble",
        tool="Seedream",
        model="example-model",
        parameters={"aspect_ratio": "9:16"},
        notes="Key visual generation",
    )
    assert req.tool == "Seedream"


def test_prompt_request_tool_too_long():
    from pydantic import ValidationError

    from app.schemas.project import PromptItemRequest

    with pytest.raises(ValidationError):
        PromptItemRequest(deliverable_id="X", prompt="p", tool="t" * 101)


# ── Media validation unit (service-level, mocked deliverable) ──


def test_validate_media_upload_rejects_bad_mime():
    from unittest.mock import MagicMock

    from app.services.project import ProjectService, UnsupportedMediaTypeError

    d = MagicMock()
    d.type = DeliverableType.IMAGE
    d.config = {}

    svc = ProjectService.__new__(ProjectService)
    with pytest.raises(UnsupportedMediaTypeError):
        svc._validate_media_upload(d, b"\x89PNG\r\n\x1a\n" + b"\x00" * 8, "application/zip")


def test_validate_media_upload_rejects_spoofed_content():
    from unittest.mock import MagicMock

    from app.services.project import ContentTypeMismatchError, ProjectService

    d = MagicMock()
    d.type = DeliverableType.IMAGE
    d.config = {}

    svc = ProjectService.__new__(ProjectService)
    # Declared PNG but content is plain text
    with pytest.raises(ContentTypeMismatchError):
        svc._validate_media_upload(d, b"#!/bin/sh rm -rf /", "image/png")


def test_validate_media_upload_accepts_valid_png():
    from unittest.mock import MagicMock

    from app.services.project import ProjectService

    d = MagicMock()
    d.type = DeliverableType.IMAGE
    d.config = {}

    svc = ProjectService.__new__(ProjectService)
    svc._validate_media_upload(d, b"\x89PNG\r\n\x1a\n" + b"\x00" * 100, "image/png")


def test_validate_media_upload_config_cannot_widen_whitelist():
    from unittest.mock import MagicMock

    from app.services.project import ProjectService, UnsupportedMediaTypeError

    d = MagicMock()
    d.type = DeliverableType.IMAGE
    # Instructor tries to allow zip files on an image deliverable
    d.config = {"accepted_formats": ["application/zip", "image/png"]}

    svc = ProjectService.__new__(ProjectService)
    with pytest.raises(UnsupportedMediaTypeError):
        svc._validate_media_upload(d, b"PK\x03\x04" + b"\x00" * 8, "application/zip")


def test_validate_media_upload_config_narrows():
    from unittest.mock import MagicMock

    from app.services.project import ProjectService, UnsupportedMediaTypeError

    d = MagicMock()
    d.type = DeliverableType.IMAGE
    d.config = {"accepted_formats": ["image/png"]}

    svc = ProjectService.__new__(ProjectService)
    # JPEG blocked because config narrowed to PNG only
    with pytest.raises(UnsupportedMediaTypeError):
        svc._validate_media_upload(d, b"\xff\xd8\xff\xe0" + b"\x00" * 8, "image/jpeg")


def test_validate_media_upload_size_config():
    from unittest.mock import MagicMock

    from app.services.project import FileTooLargeError, ProjectService

    d = MagicMock()
    d.type = DeliverableType.IMAGE
    d.config = {"max_file_size_mb": 1}

    svc = ProjectService.__new__(ProjectService)
    big = b"\x89PNG\r\n\x1a\n" + b"\x00" * (1024 * 1024 + 100)
    with pytest.raises(FileTooLargeError):
        svc._validate_media_upload(d, big, "image/png")


def test_validate_media_upload_file_type_unrestricted():
    from unittest.mock import MagicMock

    from app.services.project import ProjectService

    d = MagicMock()
    d.type = DeliverableType.FILE
    d.config = {}

    svc = ProjectService.__new__(ProjectService)
    # FILE deliverables accept anything (back-compat)
    svc._validate_media_upload(d, b"anything at all", "application/zip")


# ── Storage: raw object keys must not leak to clients ──


def test_submission_item_response_hides_file_key():
    """file_key (raw S3 path) must not be a field on the response schema."""
    from app.schemas.project import SubmissionItemResponse

    assert "file_key" not in SubmissionItemResponse.model_fields
    assert "has_file" in SubmissionItemResponse.model_fields


def test_file_response_hides_file_key():
    from app.schemas.project import FileResponse

    assert "file_key" not in FileResponse.model_fields


def test_submission_item_response_has_file_flag():
    """has_file reflects presence of a file_key on the ORM object."""
    from types import SimpleNamespace

    from app.schemas.project import SubmissionItemResponse

    with_file = SimpleNamespace(
        id="i1",
        deliverable_id="d1",
        type="file",
        content=None,
        file_key="orgs/x/submissions/y/z/abc_file.png",
        file_name="file.png",
        file_size=10,
        mime_type="image/png",
        version=1,
        note=None,
        uploaded_by="u1",
        created_at=__import__("datetime").datetime.now(),
    )
    r = SubmissionItemResponse.model_validate(with_file)
    assert r.has_file is True
    assert not hasattr(r, "file_key")

    text_item = SimpleNamespace(
        id="i2",
        deliverable_id="d1",
        type="text",
        content="hello",
        file_key=None,
        file_name=None,
        file_size=None,
        mime_type=None,
        version=1,
        note=None,
        uploaded_by="u1",
        created_at=__import__("datetime").datetime.now(),
    )
    r2 = SubmissionItemResponse.model_validate(text_item)
    assert r2.has_file is False


# ── Prompt schema: industry fields ──


def test_prompt_request_industry_fields_valid():
    from app.schemas.project import PromptItemRequest

    req = PromptItemRequest(
        deliverable_id="X",
        prompt="a shot",
        negative_prompt="blurry",
        seed=2049363429,
        cfg_scale=4.5,
        steps=30,
        sampler="Euler a",
        resources=[
            {"type": "checkpoint", "name": "WAI-illustrious", "version": "v17.0"},
            {"type": "lora", "name": "style-x", "weight": 0.8},
        ],
    )
    assert req.seed == 2049363429
    assert req.resources[1]["weight"] == 0.8


def test_prompt_request_seed_out_of_range():
    from pydantic import ValidationError

    from app.schemas.project import PromptItemRequest

    with pytest.raises(ValidationError):
        PromptItemRequest(deliverable_id="X", prompt="p", seed=2**32)
    with pytest.raises(ValidationError):
        PromptItemRequest(deliverable_id="X", prompt="p", seed=-1)


def test_prompt_request_too_many_resources():
    from pydantic import ValidationError

    from app.schemas.project import PromptItemRequest

    with pytest.raises(ValidationError):
        PromptItemRequest(
            deliverable_id="X",
            prompt="p",
            resources=[{"type": "lora", "name": f"r{i}"} for i in range(21)],
        )


def test_prompt_request_bad_resource_shape():
    from pydantic import ValidationError

    from app.schemas.project import PromptItemRequest

    with pytest.raises(ValidationError):
        PromptItemRequest(deliverable_id="X", prompt="p", resources=[{"name": "no type"}])
    with pytest.raises(ValidationError):
        PromptItemRequest(
            deliverable_id="X",
            prompt="p",
            resources=[{"type": "lora", "name": "x", "weight": 99}],
        )


def test_prompt_request_negative_prompt_cap():
    from pydantic import ValidationError

    from app.schemas.project import PromptItemRequest

    with pytest.raises(ValidationError):
        PromptItemRequest(deliverable_id="X", prompt="p", negative_prompt="n" * 10001)


def test_prompt_request_cfg_steps_bounds():
    from pydantic import ValidationError

    from app.schemas.project import PromptItemRequest

    with pytest.raises(ValidationError):
        PromptItemRequest(deliverable_id="X", prompt="p", cfg_scale=101)
    with pytest.raises(ValidationError):
        PromptItemRequest(deliverable_id="X", prompt="p", steps=1001)
