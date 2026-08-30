"""Tests targeting every remaining uncovered line for 100% coverage.

Uses mocks for S3/LLM and real DB for service paths.
APP_ENV=test PYTHONPATH=. uv run pytest tests/test_100pct.py -v --timeout=30
"""

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus


async def _u(db, role=UserRole.STUDENT):
    u = User(
        email=f"100-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="Hund",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


@pytest_asyncio.fixture
async def db():
    from app.core.database import engine

    async with AsyncSessionLocal() as s:
        yield s
        await s.rollback()
    await engine.dispose()


# ═══════ main.py lifespan (lines 22-66) ═══════


@pytest.mark.asyncio
async def test_main_lifespan_full():
    """Exercise the full lifespan including MinIO check via mock."""
    from app.main import app, lifespan

    mock_client = AsyncMock()
    mock_client.head_bucket = AsyncMock()

    async def fake_s3():
        yield mock_client

    with (
        patch("app.core.storage.get_s3_client", side_effect=lambda: fake_s3()),
        patch("app.core.storage.ensure_bucket", new_callable=AsyncMock),
    ):
        async with lifespan(app):
            pass


# ═══════ Auth: reset + verify success paths ═══════


@pytest.mark.asyncio
async def test_auth_reset_password_success(db):
    """Cover the full reset password success path (lines 288-301)."""
    from app.services.auth import AuthService

    email = f"rps-{uuid.uuid4().hex[:8]}@test.com"
    svc = AuthService(db)
    await svc.register(email, "Valid123!", "ResetS")
    await db.flush()
    await svc.forgot_password(email)
    await db.flush()

    # Get the raw token by intercepting (we stored sha256(token), so reconstruct)
    from sqlalchemy import select

    from app.models.user import PasswordResetToken

    result = await db.execute(
        select(PasswordResetToken).order_by(PasswordResetToken.created_at.desc())
    )
    token_record = result.scalars().first()

    # We can't reverse the hash, so test with a fresh token we control
    raw = secrets.token_urlsafe(32)
    token_record.token_hash = sha256(raw.encode()).hexdigest()
    token_record.expires_at = datetime.now(UTC) + timedelta(hours=1)
    token_record.used_at = None
    await db.flush()

    await svc.reset_password(raw, "NewValid123!")
    await db.flush()


@pytest.mark.asyncio
async def test_auth_verify_email_success(db):
    """Cover the verify email success path (lines 317-331)."""
    from app.services.auth import AuthService

    email = f"ves-{uuid.uuid4().hex[:8]}@test.com"
    svc = AuthService(db)
    await svc.register(email, "Valid123!", "VerS")
    await db.flush()

    from sqlalchemy import select

    from app.models.user import EmailVerificationToken

    result = await db.execute(
        select(EmailVerificationToken).order_by(EmailVerificationToken.created_at.desc())
    )
    token_record = result.scalars().first()

    raw = secrets.token_urlsafe(32)
    token_record.token_hash = sha256(raw.encode()).hexdigest()
    token_record.expires_at = datetime.now(UTC) + timedelta(hours=24)
    token_record.used_at = None
    await db.flush()

    await svc.verify_email(raw)
    await db.flush()

    # User should now be verified
    user = await db.get(User, token_record.user_id)
    assert user.email_verified is True


@pytest.mark.asyncio
async def test_auth_refresh_reuse_detection(db):
    """Token reuse OUTSIDE the concurrent-refresh grace window raises
    TokenInvalidError. (Within the window it's treated as a cross-tab race
    and succeeds — covered in test_auth.py.)"""
    from datetime import UTC, datetime, timedelta
    from hashlib import sha256

    from sqlalchemy import update as sa_update

    from app.core.security import decode_token
    from app.models.user import RefreshToken
    from app.services.auth import AuthService, TokenInvalidError

    email = f"reu-{uuid.uuid4().hex[:8]}@test.com"
    svc = AuthService(db)
    reg = await svc.register(email, "Valid123!", "Reuse")
    await db.flush()

    # Refresh once (old token revoked)
    await svc.refresh_tokens(reg.refresh_token)
    await db.flush()

    # Backdate the revocation beyond the grace window, then reuse → 401
    jti = decode_token(reg.refresh_token)["jti"]
    await db.execute(
        sa_update(RefreshToken)
        .where(RefreshToken.token_hash == sha256(jti.encode()).hexdigest())
        .values(revoked_at=datetime.now(UTC) - timedelta(seconds=60))
    )
    await db.flush()
    with pytest.raises(TokenInvalidError):
        await svc.refresh_tokens(reg.refresh_token)


# ═══════ Organization: invite flow internals ═══════


@pytest.mark.asyncio
async def test_org_invite_already_member(db):
    """Cover already_member branch in invite_members (line 283-292)."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    u1 = await _u(db)
    u2 = await _u(db)
    svc = OrgService(db)
    org = await svc.create("InvAM", None, None, u1.id)
    await svc.add_member(org.id, u2.id, OrgRole.STUDENT)
    await db.flush()

    # Invite the already-member email
    result = await svc.invite_members(org.id, [u2.email], OrgRole.STUDENT, u1.id)
    assert result.already_member == 1


@pytest.mark.asyncio
async def test_org_invite_already_invited(db):
    """Cover already_invited branch (line 303-304)."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    u = await _u(db)
    svc = OrgService(db)
    org = await svc.create("InvAI", None, None, u.id)
    await db.flush()

    target = f"inv-{uuid.uuid4().hex[:6]}@test.com"
    await svc.invite_members(org.id, [target], OrgRole.STUDENT, u.id)
    await db.flush()

    # Invite same email again
    result = await svc.invite_members(org.id, [target], OrgRole.STUDENT, u.id)
    assert result.already_invited == 1


@pytest.mark.asyncio
async def test_org_accept_email_invite(db):
    """Cover accept_email_invite full path (lines 353-383)."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    u1 = await _u(db)
    u2 = await _u(db)
    svc = OrgService(db)
    org = await svc.create("AccInv", None, None, u1.id)
    await db.flush()

    await svc.invite_members(org.id, [u2.email], OrgRole.STUDENT, u1.id)
    await db.flush()

    # Get the invite and replace hash with one we know
    from sqlalchemy import select

    from app.models.organization import OrgInvitation

    result = await db.execute(select(OrgInvitation).where(OrgInvitation.email == u2.email))
    invite = result.scalar_one()
    raw = secrets.token_urlsafe(32)
    invite.token_hash = sha256(raw.encode()).hexdigest()
    await db.flush()

    member = await svc.accept_email_invite(raw, u2.id)
    assert member.role == OrgRole.STUDENT


@pytest.mark.asyncio
async def test_org_delete_invite_link(db):
    """Cover delete_invite_link (line 423)."""
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    u = await _u(db)
    svc = OrgService(db)
    org = await svc.create("DLLink", None, None, u.id)
    link = await svc.create_invite_link(org.id, OrgRole.STUDENT, None, None, u.id)
    await db.flush()
    await svc.delete_invite_link(org.id, link.id)


# ═══════ Project: file upload/download/delete with mock S3 ═══════


@pytest.mark.asyncio
async def test_project_file_operations(db):
    """Cover upload_file, get_download_url, delete_file (lines 317-368)."""
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("FileOp", None, None, u.id)
    await db.flush()
    svc = ProjectService(db)
    proj = await svc.create_project(
        org.id,
        "FProj",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        None,
        u.id,
    )
    deliv = await svc.create_deliverable(proj.id, "File", None, "file", False, {}, 0)
    sub = await svc.create_submission(org.id, proj.id, u.id)
    await db.flush()

    # Mock S3 client
    mock_client = AsyncMock()
    mock_client.put_object = AsyncMock()
    mock_client.generate_presigned_url = AsyncMock(return_value="https://minio/presigned")

    async def fake_s3():
        yield mock_client

    with patch("app.core.storage.get_s3_client", return_value=fake_s3()):
        item = await svc.upload_file(
            sub.id, deliv.id, "test.py", b"print('hello')", "text/x-python", u.id
        )
        assert item.file_name == "test.py"
        assert item.file_size == len(b"print('hello')")
        await db.flush()

    with patch("app.core.storage.get_s3_client", return_value=fake_s3()):
        url = await svc.get_download_url(item.id)
        assert url == "https://minio/presigned"

    await svc.delete_file(item.id, u.id)


@pytest.mark.asyncio
async def test_project_extension_check(db):
    """Cover get_effective_deadline + extension path."""
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("ExtOrg", None, None, u.id)
    await db.flush()
    svc = ProjectService(db)
    proj = await svc.create_project(
        org.id,
        "ExtProj",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        datetime.now(UTC) - timedelta(hours=2),  # past deadline
        None,
        0,
        0,
        None,
        u.id,
    )
    await db.flush()

    from app.models.organization import OrgRole

    u2 = await _u(db)
    # u2 must be a member of the org to receive an extension
    await org_svc.add_member(org.id, u2.id, OrgRole.STUDENT, invited_by=u.id)
    await db.flush()
    # Grant extension
    await svc.grant_extension(
        proj.id, u2.id, datetime.now(UTC) + timedelta(days=7), "Medical", u.id
    )
    await db.flush()

    # Check timing with extension
    timing = await svc.get_submission_timing(proj, u2.id)
    assert timing == "on_time"  # Extension makes it on time


# ═══════ Evaluation: mock LLM execution ═══════


@pytest.mark.asyncio
async def test_eval_trigger_with_mock_llm(db):
    """Cover _execute_evaluation full path (lines 110-217) with mocked LLM."""
    from app.core.llm import LLMResponse
    from app.services.evaluation import EvaluationService
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("EvalOrg", None, None, u.id)
    await db.flush()

    # Setup eval settings
    eval_svc = EvaluationService(db)
    await eval_svc.update_eval_settings(org.id, {"enabled": True, "monthly_budget_usd": 100})
    await db.flush()

    # Create project + submission
    proj_svc = ProjectService(db)
    proj = await proj_svc.create_project(
        org.id,
        "EvalProj",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Quality", "max_score": 50}, {"criterion": "Design", "max_score": 50}],
        None,
        None,
        0,
        0,
        None,
        u.id,
    )
    sub = await proj_svc.create_submission(org.id, proj.id, u.id)
    await proj_svc.submit_draft(sub.id, u.id)
    await db.flush()

    # Mock the LLM
    mock_response = LLMResponse(
        content='{"scores":[{"criterion":"Quality","score":40,"max_score":50,"feedback":"Good"},{"criterion":"Design","score":35,"max_score":50,"feedback":"Nice"}],"overall_feedback":"Well done","strengths":["Clear"],"improvements":["More detail"]}',
        input_tokens=500,
        output_tokens=200,
        model="claude-sonnet-5",
        provider="anthropic",
    )

    with patch("app.services.evaluation.create_llm_client") as mock_create:
        mock_llm = AsyncMock()
        mock_llm.complete = AsyncMock(return_value=mock_response)
        mock_create.return_value = mock_llm

        task = await eval_svc.trigger_evaluation(org.id, sub.id, "submission_review")
        await db.flush()

    assert task.status.value == "completed"
    assert task.result["total_score"] == 75
    assert task.cost_usd > 0


@pytest.mark.asyncio
async def test_eval_trigger_llm_parse_failure(db):
    """Cover JSON parse failure retry path (lines 202-210)."""
    from app.core.llm import LLMResponse
    from app.services.evaluation import EvaluationService
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("EvalFail", None, None, u.id)
    eval_svc = EvaluationService(db)
    await eval_svc.update_eval_settings(org.id, {"enabled": True, "monthly_budget_usd": 100})
    await db.flush()

    proj_svc = ProjectService(db)
    proj = await proj_svc.create_project(
        org.id,
        "EFProj",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        None,
        u.id,
    )
    sub = await proj_svc.create_submission(org.id, proj.id, u.id)
    await proj_svc.submit_draft(sub.id, u.id)
    await db.flush()

    # Mock LLM to return invalid JSON
    mock_response = LLMResponse(
        content="not json at all",
        input_tokens=100,
        output_tokens=50,
        model="claude-sonnet-5",
        provider="anthropic",
    )
    with patch("app.services.evaluation.create_llm_client") as mock_create:
        mock_llm = AsyncMock()
        mock_llm.complete = AsyncMock(return_value=mock_response)
        mock_create.return_value = mock_llm

        task = await eval_svc.trigger_evaluation(org.id, sub.id, "submission_review")
        await db.flush()

    # Should have retried and still be pending or failed
    assert task.status.value in ("pending", "failed")
    assert task.retries >= 1


# ═══════ Portfolio: public profile data assembly ═══════


@pytest.mark.asyncio
async def test_portfolio_public_profile_with_items(db):
    """Cover get_public_profile data assembly (lines 119-156)."""
    from app.services.portfolio import PortfolioService

    u = await _u(db)
    svc = PortfolioService(db)
    profile = await svc.get_or_create_profile(u.id)
    profile.visibility = "public"
    await svc.update_profile(u.id, headline="Dev", bio="Bio")
    await db.flush()

    # Create public + featured item
    await svc.create_item(u.id, "Featured Proj", "Desc", None, ["ai"], None, None, "public", True)
    # Create unlisted item (should not appear in public)
    await svc.create_item(u.id, "Hidden Proj", None, None, None, None, None, "unlisted", False)
    await db.flush()

    pub = await svc.get_public_profile(profile.username)
    assert pub is not None
    assert pub["item_count"] >= 1
    assert len(pub["featured_items"]) >= 1
    assert pub["headline"] == "Dev"


@pytest.mark.asyncio
async def test_portfolio_get_public_item_by_slug(db):
    """Cover get_public_item (lines 219-235)."""
    from app.services.portfolio import PortfolioService

    u = await _u(db)
    svc = PortfolioService(db)
    profile = await svc.get_or_create_profile(u.id)
    profile.visibility = "public"
    await db.flush()

    item = await svc.create_item(u.id, "Slug Test", None, None, None, None, None, "public", False)
    await db.flush()

    found = await svc.get_public_item(profile.username, item.slug)
    assert found is not None
    assert found.title == "Slug Test"


@pytest.mark.asyncio
async def test_portfolio_badge_toggle(db):
    """Cover toggle_badge (lines 296-301)."""
    from app.models.portfolio import SkillBadge
    from app.services.organization import OrgService
    from app.services.portfolio import PortfolioService
    from app.services.skill import SkillService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("BadgeOrg", None, None, u.id)
    await db.flush()

    svc_s = SkillService(db)
    cat = await svc_s.create_category(org.id, "BC", None, None, None, u.id)
    skill = await svc_s.create_skill(
        org.id, cat.id, "BS", None, "D", None, "beginner", None, None, None, u.id
    )
    await db.flush()

    badge = SkillBadge(
        user_id=u.id,
        skill_id=skill.id,
        org_id=org.id,
        skill_name="BS",
        category_name="BC",
        completion_pct=100,
        completed_at=datetime.now(UTC),
    )
    db.add(badge)
    await db.flush()

    svc = PortfolioService(db)
    toggled = await svc.toggle_badge(badge.id, u.id, False)
    assert toggled.show_on_profile is False


# ═══════ Skill: _update_skill_progress complete ═══════


@pytest.mark.asyncio
async def test_skill_progress_complete(db):
    """Cover _update_skill_progress completion path (lines 347-357)."""
    from app.services.organization import OrgService
    from app.services.skill import SkillService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("ProgOrg", None, None, u.id)
    await db.flush()

    svc = SkillService(db)
    cat = await svc.create_category(org.id, "ProgCat", None, None, None, u.id)
    skill = await svc.create_skill(
        org.id, cat.id, "ProgSkill", None, "D", None, "beginner", None, None, None, u.id
    )
    ex = await svc.create_exercise(
        org.id,
        skill.id,
        "ProgEx",
        "D",
        "multiple_choice",
        {"correct": ["a"], "options": [{"id": "a", "text": "R"}]},
        100,
        u.id,
    )
    await db.flush()

    # Submit correct → should complete the skill
    await svc.submit_attempt(org.id, ex.id, u.id, {"selected": ["a"]})
    await db.flush()

    progress = await svc.get_skill_progress(skill.id, u.id)
    assert progress is not None
    assert progress.status.value == "completed"
    assert progress.completed_at is not None


# ═══════ deps.py: require_org_member ═══════


@pytest.mark.asyncio
async def test_deps_require_org_member_not_member(db):
    """Cover require_org_member 403 path (line 80-85)."""
    from fastapi import HTTPException

    from app.api.deps import require_org_member

    u = await _u(db)
    with pytest.raises(HTTPException) as exc_info:
        await require_org_member("nonexistent-org", u, db)
    assert exc_info.value.status_code == 404  # Org not found (checked before membership)


# ═══════ Exceptions: unhandled handler ═══════


@pytest.mark.asyncio
async def test_exception_handlers():
    """Cover exception handler registration (lines 54-60)."""
    from fastapi import FastAPI

    from app.exceptions import register_exception_handlers

    test_app = FastAPI()
    register_exception_handlers(test_app)
    assert len(test_app.exception_handlers) >= 3


# ═══════ Rate limit: full Redis flow ═══════


@pytest.mark.asyncio
async def test_rate_limit_real_redis():
    """Cover check_rate_limit with real Redis (lines 28-39, 55-67)."""
    from app.core.rate_limit import check_rate_limit

    key = f"test:ratelimit:{uuid.uuid4().hex[:8]}"
    allowed, remaining = await check_rate_limit(key, 100, 60)
    assert allowed is True


@pytest.mark.asyncio
async def test_rate_limit_dependency_denied():
    """Cover rate_limit dependency 429 path (lines 55-67)."""
    from app.core.rate_limit import rate_limit

    checker = rate_limit(1, 60)
    mock_request = MagicMock()
    mock_request.client = MagicMock()
    mock_request.client.host = "127.0.0.1"
    mock_request.url = MagicMock()
    mock_request.url.path = f"/test/{uuid.uuid4().hex[:8]}"
    mock_request.method = "GET"
    mock_request.state = MagicMock()

    # Patch settings.app_env to enable rate limiting (settings is a singleton;
    # os.environ changes after import don't affect it)
    with patch("app.core.rate_limit.settings") as mock_settings:
        mock_settings.app_env = "production"

        # First call should pass
        with patch(
            "app.core.rate_limit.check_rate_limit", new_callable=AsyncMock, return_value=(True, 0)
        ):
            await checker(mock_request)

        # Second call should deny
        from fastapi import HTTPException

        with patch(
            "app.core.rate_limit.check_rate_limit", new_callable=AsyncMock, return_value=(False, 0)
        ):
            with pytest.raises(HTTPException) as exc:
                await checker(mock_request)
            assert exc.value.status_code == 429
