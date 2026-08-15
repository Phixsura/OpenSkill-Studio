"""DB integration tests for templates, media uploads, versioning, assets, prompts.

Requires PostgreSQL + MinIO running (make infra-up && make db-migrate).
APP_ENV=test PYTHONPATH=. uv run pytest tests/test_media_db.py -v
"""

import json
import uuid

import pytest
import pytest_asyncio

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole
from app.models.project import DeliverableType
from app.models.user import User, UserRole, UserStatus
from app.services.project import (
    ContentTypeMismatchError,
    FileTooLargeError,
    MaxFilesReachedError,
    ProjectService,
    TemplateNotFoundError,
    UnsupportedMediaTypeError,
)

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100
MP4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 100
MP3 = b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"\x00" * 100


@pytest_asyncio.fixture
async def db():
    from app.core.database import engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, role=UserRole.STUDENT):
    u = User(
        email=f"media-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="MediaTest",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org_with_member(db, user, role=OrgRole.OWNER):
    org = Organization(
        name=f"MediaOrg-{uuid.uuid4().hex[:6]}",
        slug=f"media-{uuid.uuid4().hex[:8]}",
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=user.id, role=role, status=MemberStatus.ACTIVE))
    await db.flush()
    return org


async def _setup(db):
    user = await _user(db)
    org = await _org_with_member(db, user)
    svc = ProjectService(db)
    return user, org, svc


# ══════════════════════════════════════════════════════════
# Templates
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_template_crud(db):
    user, org, svc = await _setup(db)

    t = await svc.create_template(
        org.id,
        user.id,
        name="Custom Template",
        description="desc",
        instructions="inst",
        project_type="ai_visual",
        rubric=[{"criterion": "Q", "max_score": 100}],
        deliverables=[
            {"name": "Hero", "type": "image", "required": True, "config": {}, "sort_order": 0}
        ],
    )
    assert t.id
    assert t.project_type == "ai_visual"

    # List returns builtins + org template
    builtins, org_templates = await svc.list_templates(org.id)
    assert len(builtins) >= 1
    assert any(x.id == t.id for x in org_templates)

    # Get
    fetched = await svc.get_template(t.id, org.id)
    assert fetched.name == "Custom Template"

    # Update
    updated = await svc.update_template(t.id, org.id, name="Renamed Template")
    assert updated.name == "Renamed Template"

    # Soft delete
    await svc.delete_template(t.id, org.id)
    with pytest.raises(TemplateNotFoundError):
        await svc.get_template(t.id, org.id)


@pytest.mark.asyncio
async def test_template_org_isolation(db):
    """Org B must not see or fetch org A's templates."""
    user_a, org_a, svc = await _setup(db)
    user_b = await _user(db)
    org_b = await _org_with_member(db, user_b)

    t = await svc.create_template(
        org_a.id,
        user_a.id,
        name="Org A Secret Template",
        description="d",
        instructions="i",
        rubric=[{"criterion": "Q", "max_score": 100}],
        deliverables=[],
    )

    # Fetch via org B scope → not found
    with pytest.raises(TemplateNotFoundError):
        await svc.get_template(t.id, org_b.id)

    # List for org B does not include it
    _, org_b_templates = await svc.list_templates(org_b.id)
    assert not any(x.id == t.id for x in org_b_templates)


@pytest.mark.asyncio
async def test_builtin_template_get(db):
    _, org, svc = await _setup(db)
    t = await svc.get_template("builtin-ai-product-ad", org.id)
    assert isinstance(t, dict)
    assert t["name"] == "AI Product Advertisement"


@pytest.mark.asyncio
async def test_create_project_from_builtin_template(db):
    user, org, svc = await _setup(db)

    project = await svc.create_project_from_template(org.id, "builtin-ai-product-ad", user.id)
    assert project.project_type == "ai_visual"
    assert project.title == "AI Product Advertisement"

    deliverables = await svc.list_deliverables(project.id)
    assert len(deliverables) == 8
    assert deliverables[0].name == "Client Brief"
    assert deliverables[3].type == DeliverableType.PROMPT
    assert deliverables[7].type == DeliverableType.FINAL_OUTPUT


@pytest.mark.asyncio
async def test_template_project_independence(db):
    """Editing a project created from a template must not change the template."""
    user, org, svc = await _setup(db)

    t = await svc.create_template(
        org.id,
        user.id,
        name="Independence Test",
        description="original description",
        instructions="original instructions",
        rubric=[{"criterion": "Q", "max_score": 100}],
        deliverables=[
            {"name": "Stage One", "type": "text", "required": True, "config": {}, "sort_order": 0}
        ],
    )

    project = await svc.create_project_from_template(org.id, t.id, user.id)

    # Mutate the project + its deliverables
    await svc.update_project(project.id, description="CHANGED")
    deliverables = await svc.list_deliverables(project.id)
    await svc.update_deliverable(deliverables[0].id, name="CHANGED STAGE")

    # Template untouched
    fresh = await svc.get_template(t.id, org.id)
    assert fresh.description == "original description"
    assert fresh.deliverables[0]["name"] == "Stage One"


@pytest.mark.asyncio
async def test_builtin_template_readonly(db):
    from app.exceptions import AppError

    user, org, svc = await _setup(db)
    with pytest.raises(AppError) as exc:
        await svc.update_template("builtin-ai-product-ad", org.id, name="Hacked")
    assert exc.value.code == "BUILTIN_READONLY"

    with pytest.raises(AppError) as exc:
        await svc.delete_template("builtin-ai-product-ad", org.id)
    assert exc.value.code == "BUILTIN_READONLY"


# ══════════════════════════════════════════════════════════
# Media uploads + versioning
# ══════════════════════════════════════════════════════════


async def _project_with_deliverable(svc, org, user, dtype="image", config=None):
    project = await svc.create_project(
        org_id=org.id,
        title=f"Media Project {uuid.uuid4().hex[:6]}",
        slug=None,
        description="d",
        instructions="i",
        difficulty="beginner",
        max_score=100,
        rubric=[{"criterion": "Q", "max_score": 100}],
        deadline=None,
        late_deadline=None,
        late_penalty_pct=0,
        max_submissions=0,
        skill_ids=None,
        created_by=user.id,
        project_type="ai_visual",
    )
    d = await svc.create_deliverable(project.id, "Media Slot", None, dtype, True, config or {}, 0)
    sub = await svc.create_submission(org.id, project.id, user.id)
    return project, d, sub


@pytest.mark.asyncio
async def test_upload_image_happy_path(db):
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")

    item = await svc.upload_file(sub.id, d.id, "hero.png", PNG, "image/png", user.id)
    assert item.version == 1
    assert item.mime_type == "image/png"
    assert item.file_key.startswith(f"orgs/{org.id}/submissions/")


@pytest.mark.asyncio
async def test_upload_video_happy_path(db):
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "video")
    item = await svc.upload_file(sub.id, d.id, "clip.mp4", MP4, "video/mp4", user.id)
    assert item.version == 1


@pytest.mark.asyncio
async def test_upload_audio_happy_path(db):
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "audio")
    item = await svc.upload_file(sub.id, d.id, "track.mp3", MP3, "audio/mpeg", user.id)
    assert item.version == 1


@pytest.mark.asyncio
async def test_upload_wrong_mime_rejected(db):
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")
    with pytest.raises(UnsupportedMediaTypeError):
        await svc.upload_file(sub.id, d.id, "clip.mp4", MP4, "video/mp4", user.id)


@pytest.mark.asyncio
async def test_upload_spoofed_content_rejected(db):
    """Text content declared as PNG must be rejected by magic-byte check."""
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")
    with pytest.raises(ContentTypeMismatchError):
        await svc.upload_file(
            sub.id, d.id, "fake.png", b"<script>alert(1)</script>" * 4, "image/png", user.id
        )


@pytest.mark.asyncio
async def test_upload_oversized_rejected(db):
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image", {"max_file_size_mb": 1})
    big_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * (1024 * 1024 + 100)
    with pytest.raises(FileTooLargeError):
        await svc.upload_file(sub.id, d.id, "big.png", big_png, "image/png", user.id)


@pytest.mark.asyncio
async def test_upload_max_files_enforced(db):
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image", {"max_files": 2})

    await svc.upload_file(sub.id, d.id, "a.png", PNG, "image/png", user.id)
    await svc.upload_file(sub.id, d.id, "b.png", PNG, "image/png", user.id)
    with pytest.raises(MaxFilesReachedError):
        await svc.upload_file(sub.id, d.id, "c.png", PNG, "image/png", user.id)


@pytest.mark.asyncio
async def test_upload_path_traversal_sanitized(db):
    """A malicious filename must not escape the object-key prefix."""
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")
    item = await svc.upload_file(sub.id, d.id, "../../../etc/passwd.png", PNG, "image/png", user.id)
    prefix = f"orgs/{org.id}/submissions/{sub.id}/{d.id}/"
    # Key stays within the submission prefix
    assert item.file_key.startswith(prefix)
    # The sanitized filename (everything after the prefix) has NO path
    # separators — so ".." cannot traverse; it's just literal dots in a
    # flat name. This is the actual anti-traversal property.
    tail = item.file_key[len(prefix) :]
    assert "/" not in tail
    assert "\\" not in tail
    assert "/etc/" not in item.file_key


@pytest.mark.asyncio
async def test_version_history_preserved(db):
    """Re-uploading to the same deliverable increments version, keeps old rows."""
    from sqlalchemy import select

    from app.models.project import SubmissionItem

    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image", {"max_files": 1})

    v1 = await svc.upload_file(sub.id, d.id, "v1.png", PNG, "image/png", user.id)
    v2 = await svc.upload_file(
        sub.id, d.id, "v2.png", PNG, "image/png", user.id, note="fixed color"
    )
    v3 = await svc.upload_file(sub.id, d.id, "v3.png", PNG, "image/png", user.id)

    assert (v1.version, v2.version, v3.version) == (1, 2, 3)
    assert v2.note == "fixed color"
    # §7: each version records its uploader
    assert v1.uploaded_by == user.id
    assert v2.uploaded_by == user.id

    result = await db.execute(
        select(SubmissionItem).where(
            SubmissionItem.submission_id == sub.id,
            SubmissionItem.deliverable_id == d.id,
        )
    )
    items = list(result.scalars().all())
    assert len(items) == 3  # all versions preserved


@pytest.mark.asyncio
async def test_upload_to_foreign_deliverable_rejected(db):
    """Deliverable from another project cannot receive uploads."""
    from app.services.project import DeliverableNotFoundError

    user, org, svc = await _setup(db)
    _, _, sub = await _project_with_deliverable(svc, org, user, "image")
    _, other_d, _ = await _project_with_deliverable(svc, org, user, "image")

    with pytest.raises(DeliverableNotFoundError):
        await svc.upload_file(sub.id, other_d.id, "x.png", PNG, "image/png", user.id)


@pytest.mark.asyncio
async def test_file_deliverable_type_unrestricted(db):
    """Legacy FILE deliverables accept any content type (back-compat)."""
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "file")
    item = await svc.upload_file(
        sub.id, d.id, "anything.zip", b"PK\x03\x04" + b"\x00" * 50, "application/zip", user.id
    )
    assert item.version == 1


# ══════════════════════════════════════════════════════════
# Assets
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_asset_upload_and_list(db):
    user, org, svc = await _setup(db)
    project, _, _ = await _project_with_deliverable(svc, org, user)

    asset = await svc.upload_asset(
        org.id, project.id, "Brand Logo", "Use in all shots", "logo.png", PNG, "image/png", user.id
    )
    assert asset.file_key.startswith(f"orgs/{org.id}/projects/{project.id}/assets/")

    assets = await svc.list_assets(project.id)
    assert len(assets) == 1
    assert assets[0].name == "Brand Logo"

    url = await svc.get_asset_download_url(asset.id, org.id)
    assert "http" in url


@pytest.mark.asyncio
async def test_asset_rejects_non_media(db):
    user, org, svc = await _setup(db)
    project, _, _ = await _project_with_deliverable(svc, org, user)
    with pytest.raises(UnsupportedMediaTypeError):
        await svc.upload_asset(
            org.id,
            project.id,
            "Bad",
            None,
            "x.zip",
            b"PK\x03\x04" + b"\x00" * 20,
            "application/zip",
            user.id,
        )


@pytest.mark.asyncio
async def test_asset_rejects_spoofed_content(db):
    user, org, svc = await _setup(db)
    project, _, _ = await _project_with_deliverable(svc, org, user)
    with pytest.raises(ContentTypeMismatchError):
        await svc.upload_asset(
            org.id,
            project.id,
            "Spoof",
            None,
            "fake.png",
            b"not a png at all!!",
            "image/png",
            user.id,
        )


@pytest.mark.asyncio
async def test_asset_org_isolation(db):
    from app.services.project import AssetNotFoundError

    user_a, org_a, svc = await _setup(db)
    project, _, _ = await _project_with_deliverable(svc, org_a, user_a)
    asset = await svc.upload_asset(
        org_a.id, project.id, "Secret", None, "s.png", PNG, "image/png", user_a.id
    )

    user_b = await _user(db)
    org_b = await _org_with_member(db, user_b)

    # Access via org B scope → not found
    with pytest.raises(AssetNotFoundError):
        await svc.get_asset(asset.id, org_b.id)
    with pytest.raises(AssetNotFoundError):
        await svc.get_asset_download_url(asset.id, org_b.id)


@pytest.mark.asyncio
async def test_asset_delete(db):
    user, org, svc = await _setup(db)
    project, _, _ = await _project_with_deliverable(svc, org, user)
    asset = await svc.upload_asset(
        org.id, project.id, "Temp", None, "t.png", PNG, "image/png", user.id
    )
    await svc.delete_asset(asset.id, org.id)
    assets = await svc.list_assets(project.id)
    assert len(assets) == 0


# ══════════════════════════════════════════════════════════
# Prompt items
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_prompt_item_stored_and_versioned(db):
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "prompt")

    data = {
        "prompt": "Create a cinematic product shot of a watch",
        "tool": "Seedream",
        "model": "example-model",
        "parameters": {"aspect_ratio": "9:16"},
        "notes": "key visual",
    }
    item = await svc.add_prompt_item(sub.id, d.id, data, user.id)
    assert item.version == 1
    parsed = json.loads(item.content)
    assert parsed["prompt"] == data["prompt"]
    assert parsed["parameters"]["aspect_ratio"] == "9:16"

    # Second prompt → v2
    item2 = await svc.add_prompt_item(sub.id, d.id, {**data, "prompt": "Refined"}, user.id)
    assert item2.version == 2


@pytest.mark.asyncio
async def test_prompt_item_wrong_deliverable_type(db):
    from app.exceptions import AppError

    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")

    with pytest.raises(AppError) as exc:
        await svc.add_prompt_item(sub.id, d.id, {"prompt": "x"}, user.id)
    assert exc.value.code == "INVALID_TYPE"


@pytest.mark.asyncio
async def test_prompt_item_not_owner(db):
    from app.exceptions import AppError

    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "prompt")
    stranger = await _user(db)

    with pytest.raises(AppError) as exc:
        await svc.add_prompt_item(sub.id, d.id, {"prompt": "x"}, stranger.id)
    assert exc.value.status_code == 403


# ══════════════════════════════════════════════════════════
# Full E2E: template → project → prompt + media → versions → review
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_ai_visual_e2e_flow(db):
    """Instructor creates from builtin → learner completes workflow →
    replaces an image → instructor reviews → approved."""
    instructor = await _user(db, UserRole.INSTRUCTOR)
    org = await _org_with_member(db, instructor, OrgRole.INSTRUCTOR)
    svc = ProjectService(db)

    # Learner joins org
    learner = await _user(db)
    db.add(
        OrgMember(
            org_id=org.id, user_id=learner.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE
        )
    )
    await db.flush()

    # 1. Instructor creates project from builtin template + publishes
    project = await svc.create_project_from_template(org.id, "builtin-ai-product-ad", instructor.id)
    await svc.publish_project(project.id)
    deliverables = await svc.list_deliverables(project.id)
    by_name = {d.name: d for d in deliverables}

    # 2. Learner starts a submission
    sub = await svc.create_submission(org.id, project.id, learner.id)

    # 3. Learner submits prompt
    prompt_item = await svc.add_prompt_item(
        sub.id,
        by_name["Prompt Design"].id,
        {"prompt": "Cinematic watch on marble, dramatic light", "tool": "Seedream"},
        learner.id,
    )
    assert prompt_item.version == 1

    # 4. Learner uploads key visual (PNG)
    kv1 = await svc.upload_file(
        sub.id, by_name["Key Visuals"].id, "kv.png", PNG, "image/png", learner.id
    )
    assert kv1.version == 1

    # 5. Learner uploads storyboard image + video clip + final video
    await svc.upload_file(sub.id, by_name["Storyboard"].id, "sb1.png", PNG, "image/png", learner.id)
    await svc.upload_file(
        sub.id, by_name["Video Clips"].id, "clip.mp4", MP4, "video/mp4", learner.id
    )
    await svc.upload_file(
        sub.id, by_name["Final Video"].id, "final.mp4", MP4, "video/mp4", learner.id
    )

    # 6. Learner replaces the key visual → v2; v1 remains
    kv2 = await svc.upload_file(
        sub.id,
        by_name["Key Visuals"].id,
        "kv-fixed.png",
        PNG,
        "image/png",
        learner.id,
        note="fixed lighting",
    )
    assert kv2.version == 2
    url_v1 = await svc.get_download_url(kv1.id)
    assert "http" in url_v1  # old version still accessible

    # 7. Text deliverables via items (Client Brief + Creative Concept)
    from app.models.project import ItemType, SubmissionItem

    db.add(
        SubmissionItem(
            submission_id=sub.id,
            deliverable_id=by_name["Client Brief"].id,
            type=ItemType.TEXT,
            content="Client wants a luxury watch ad",
        )
    )
    db.add(
        SubmissionItem(
            submission_id=sub.id,
            deliverable_id=by_name["Creative Concept"].id,
            type=ItemType.TEXT,
            content="# Concept\nNoir aesthetic",
        )
    )
    await db.flush()

    # 8. Submit
    submitted = await svc.submit_draft(sub.id, learner.id)
    assert submitted.status.value == "submitted"

    # 9. Instructor reviews → approved
    review = await svc.create_review(
        sub.id,
        instructor.id,
        "approved",
        92,
        {"scores": [{"criterion": "Visual Quality", "score": 23}]},
        "Excellent work",
    )
    assert review.status.value == "approved"

    fresh = await svc.get_submission(sub.id)
    assert fresh.status.value == "approved"
    assert fresh.final_score == 92


# ══════════════════════════════════════════════════════════
# Generation metadata extraction on upload
# ══════════════════════════════════════════════════════════

A1111_INFOTEXT = (
    "cinematic watch on marble, dramatic light\n"
    "Negative prompt: blurry, low quality\n"
    "Steps: 30, Sampler: Euler a, CFG scale: 4.5, Seed: 987654321, Size: 832x1216"
)


def _png_with_parameters(text: str) -> bytes:
    import struct as _s
    import zlib as _z

    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(ctype, data):
        return (
            _s.pack(">I", len(data))
            + ctype
            + data
            + _s.pack(">I", _z.crc32(ctype + data) & 0xFFFFFFFF)
        )

    ihdr = chunk(b"IHDR", _s.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
    text_chunk = chunk(b"tEXt", b"parameters\x00" + text.encode("latin-1"))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + text_chunk + iend


@pytest.mark.asyncio
async def test_upload_extracts_a1111_metadata(db):
    """PNG with embedded A1111 infotext → generation dict stored in content."""
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")

    png = _png_with_parameters(A1111_INFOTEXT)
    item = await svc.upload_file(sub.id, d.id, "gen.png", png, "image/png", user.id)

    assert item.content is not None
    parsed = json.loads(item.content)
    gen = parsed["generation"]
    assert gen["source"] == "a1111"
    assert gen["prompt"].startswith("cinematic watch")
    assert gen["negative_prompt"] == "blurry, low quality"
    assert gen["seed"] == 987654321
    assert gen["cfg_scale"] == 4.5
    assert gen["steps"] == 30
    assert gen["sampler"] == "Euler a"


@pytest.mark.asyncio
async def test_upload_plain_png_no_metadata(db):
    """PNG without embedded metadata → content stays NULL."""
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")
    item = await svc.upload_file(sub.id, d.id, "plain.png", PNG, "image/png", user.id)
    assert item.content is None


@pytest.mark.asyncio
async def test_upload_file_type_skips_extraction(db):
    """Legacy FILE deliverables don't run extraction (back-compat)."""
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "file")
    png = _png_with_parameters(A1111_INFOTEXT)
    item = await svc.upload_file(sub.id, d.id, "gen.png", png, "image/png", user.id)
    assert item.content is None


@pytest.mark.asyncio
async def test_prompt_item_industry_fields_roundtrip(db):
    """New industry fields (seed/negative/cfg/steps/sampler/resources) roundtrip."""
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "prompt")

    data = {
        "prompt": "cinematic shot",
        "negative_prompt": "blurry",
        "seed": 42,
        "cfg_scale": 7.0,
        "steps": 25,
        "sampler": "dpmpp_2m",
        "resources": [{"type": "lora", "name": "style-x", "weight": 0.8}],
    }
    item = await svc.add_prompt_item(sub.id, d.id, data, user.id)
    parsed = json.loads(item.content)
    assert parsed["seed"] == 42
    assert parsed["negative_prompt"] == "blurry"
    assert parsed["resources"][0]["weight"] == 0.8


# ══════════════════════════════════════════════════════════
# Anchored comments
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_comment_global_and_region(db):
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")
    item = await svc.upload_file(sub.id, d.id, "kv.png", PNG, "image/png", user.id)

    c1 = await svc.add_comment(org.id, sub.id, item.id, user.id, text="Nice composition")
    assert c1.anchor_type.value == "global"
    assert c1.region is None

    c2 = await svc.add_comment(
        org.id,
        sub.id,
        item.id,
        user.id,
        text="Logo is soft here",
        anchor_type="region",
        region={
            "type": "rectangle",
            "bounds": {"minX": 0.1, "minY": 0.1, "maxX": 0.4, "maxY": 0.3},
        },
    )
    assert c2.anchor_type.value == "region"
    assert c2.region["bounds"]["maxX"] == 0.4

    comments = await svc.list_comments(sub.id)
    assert len(comments) == 2


@pytest.mark.asyncio
async def test_comment_time_anchor_and_consistency(db):
    from app.exceptions import AppError

    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "video")
    item = await svc.upload_file(sub.id, d.id, "clip.mp4", MP4, "video/mp4", user.id)

    c = await svc.add_comment(
        org.id,
        sub.id,
        item.id,
        user.id,
        text="Cut is too abrupt",
        anchor_type="time",
        timestamp_ms=4200,
        duration_ms=1500,
    )
    assert c.timestamp_ms == 4200
    assert c.duration_ms == 1500

    # time anchor without timestamp → 422
    with pytest.raises(AppError) as exc:
        await svc.add_comment(org.id, sub.id, item.id, user.id, text="x", anchor_type="time")
    assert exc.value.code == "INVALID_ANCHOR"

    # region anchor without region → 422
    with pytest.raises(AppError) as exc:
        await svc.add_comment(org.id, sub.id, item.id, user.id, text="x", anchor_type="region")
    assert exc.value.code == "INVALID_ANCHOR"

    # global anchor discards stray coordinates
    c2 = await svc.add_comment(
        org.id,
        sub.id,
        item.id,
        user.id,
        text="overall",
        timestamp_ms=999,
    )
    assert c2.timestamp_ms is None


@pytest.mark.asyncio
async def test_comment_threading_one_level(db):
    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")
    item = await svc.upload_file(sub.id, d.id, "kv.png", PNG, "image/png", user.id)

    root = await svc.add_comment(org.id, sub.id, item.id, user.id, text="root")
    reply = await svc.add_comment(org.id, sub.id, item.id, user.id, text="reply", parent_id=root.id)
    assert reply.parent_id == root.id

    # Reply-to-reply flattens to the root (one-level threads)
    deep = await svc.add_comment(org.id, sub.id, item.id, user.id, text="deep", parent_id=reply.id)
    assert deep.parent_id == root.id


@pytest.mark.asyncio
async def test_comment_complete_and_delete(db):
    from app.exceptions import AppError

    user, org, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org, user, "image")
    item = await svc.upload_file(sub.id, d.id, "kv.png", PNG, "image/png", user.id)
    c = await svc.add_comment(org.id, sub.id, item.id, user.id, text="todo: fix color")

    updated = await svc.set_comment_completed(c.id, org.id, True)
    assert updated.completed is True

    # Non-author cannot delete
    stranger = await _user(db)
    with pytest.raises(AppError) as exc:
        await svc.delete_comment(c.id, org.id, stranger.id)
    assert exc.value.status_code == 403

    await svc.delete_comment(c.id, org.id, user.id)
    assert await svc.list_comments(sub.id) == []


@pytest.mark.asyncio
async def test_comment_org_isolation(db):
    from app.exceptions import AppError

    user_a, org_a, svc = await _setup(db)
    _, d, sub = await _project_with_deliverable(svc, org_a, user_a, "image")
    item = await svc.upload_file(sub.id, d.id, "kv.png", PNG, "image/png", user_a.id)
    c = await svc.add_comment(org_a.id, sub.id, item.id, user_a.id, text="secret feedback")

    user_b = await _user(db)
    org_b = await _org_with_member(db, user_b)
    with pytest.raises(AppError):
        await svc.get_comment(c.id, org_b.id)
    with pytest.raises(AppError):
        await svc.set_comment_completed(c.id, org_b.id, True)


@pytest.mark.asyncio
async def test_comment_foreign_item_rejected(db):
    from app.exceptions import AppError

    user, org, svc = await _setup(db)
    _, d1, sub1 = await _project_with_deliverable(svc, org, user, "image")
    _, d2, sub2 = await _project_with_deliverable(svc, org, user, "image")
    item2 = await svc.upload_file(sub2.id, d2.id, "other.png", PNG, "image/png", user.id)

    # Comment on sub1 referencing sub2's item → 404
    with pytest.raises(AppError) as exc:
        await svc.add_comment(org.id, sub1.id, item2.id, user.id, text="cross-item")
    assert exc.value.code == "ITEM_NOT_FOUND"
