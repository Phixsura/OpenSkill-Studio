"""Service unit tests with mocked DB sessions."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.delete = AsyncMock()
    return db


def _mock_result(value=None, scalars_list=None):
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=value)
    result.scalar_one = MagicMock(return_value=value if value is not None else 0)
    if scalars_list is not None:
        result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=scalars_list)))
    else:
        result.scalars = MagicMock(return_value=iter([]))
    result.all = MagicMock(return_value=[])
    return result


# ── AuthService ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_auth_register_duplicate():
    from app.services.auth import AuthService, EmailAlreadyExistsError

    db = _mock_db()
    existing_user = MagicMock()
    db.execute = AsyncMock(return_value=_mock_result(value=existing_user))

    svc = AuthService(db)
    with pytest.raises(EmailAlreadyExistsError):
        await svc.register("dup@test.com", "Valid123!", "Dup")


@pytest.mark.asyncio
async def test_auth_login_not_found():
    from app.services.auth import AuthService, InvalidCredentialsError

    db = _mock_db()
    db.execute = AsyncMock(return_value=_mock_result(value=None))

    svc = AuthService(db)
    with pytest.raises(InvalidCredentialsError):
        await svc.login("noone@test.com", "Pass123!")


@pytest.mark.asyncio
async def test_auth_login_suspended():
    from app.models.user import UserStatus
    from app.services.auth import AccountSuspendedError, AuthService

    db = _mock_db()
    user = MagicMock()
    user.has_password = True
    user.password_hash = "$2b$12$test"
    user.status = UserStatus.SUSPENDED
    db.execute = AsyncMock(return_value=_mock_result(value=user))

    svc = AuthService(db)
    with patch("app.services.auth.verify_password", return_value=True):
        with pytest.raises(AccountSuspendedError):
            await svc.login("sus@test.com", "Pass123!")


@pytest.mark.asyncio
async def test_auth_login_deleted():
    from app.models.user import UserStatus
    from app.services.auth import AuthService, InvalidCredentialsError

    db = _mock_db()
    user = MagicMock()
    user.has_password = True
    user.password_hash = "$2b$12$test"
    user.status = UserStatus.DELETED
    db.execute = AsyncMock(return_value=_mock_result(value=user))

    svc = AuthService(db)
    with patch("app.services.auth.verify_password", return_value=True):
        with pytest.raises(InvalidCredentialsError):
            await svc.login("del@test.com", "Pass123!")


@pytest.mark.asyncio
async def test_auth_refresh_not_refresh_type():
    from app.services.auth import AuthService, TokenInvalidError

    db = _mock_db()
    svc = AuthService(db)

    with patch(
        "app.services.auth.decode_token", return_value={"type": "access", "sub": "x", "jti": "y"}
    ):
        with pytest.raises(TokenInvalidError, match="Not a refresh"):
            await svc.refresh_tokens("fake-token")


@pytest.mark.asyncio
async def test_auth_refresh_token_not_found():
    from app.services.auth import AuthService, TokenInvalidError

    db = _mock_db()
    db.execute = AsyncMock(return_value=_mock_result(value=None))

    svc = AuthService(db)
    with patch(
        "app.services.auth.decode_token", return_value={"type": "refresh", "sub": "x", "jti": "y"}
    ):
        with pytest.raises(TokenInvalidError, match="not found"):
            await svc.refresh_tokens("fake-token")


@pytest.mark.asyncio
async def test_auth_refresh_token_reuse():
    from datetime import UTC, datetime, timedelta

    from app.services.auth import AuthService, TokenInvalidError

    db = _mock_db()
    token_record = MagicMock()
    token_record.is_revoked = True
    # Revoked OUTSIDE the concurrent-refresh grace window → reuse rejected
    token_record.revoked_at = datetime.now(UTC) - timedelta(seconds=60)
    db.execute = AsyncMock(return_value=_mock_result(value=token_record))

    svc = AuthService(db)
    svc._revoke_all_user_tokens = AsyncMock()

    with patch(
        "app.services.auth.decode_token", return_value={"type": "refresh", "sub": "x", "jti": "y"}
    ):
        with pytest.raises(TokenInvalidError):
            await svc.refresh_tokens("fake-token")


@pytest.mark.asyncio
async def test_auth_change_password_wrong_old():
    from app.services.auth import AuthService, InvalidCredentialsError

    db = _mock_db()
    user = MagicMock()
    user.has_password = True
    user.password_hash = "$2b$12$test"

    svc = AuthService(db)
    with patch("app.services.auth.verify_password", return_value=False):
        with pytest.raises(InvalidCredentialsError):
            await svc.change_password(user, "wrong", "NewPass123!")


@pytest.mark.asyncio
async def test_auth_forgot_password_no_user():
    from app.services.auth import AuthService

    db = _mock_db()
    db.execute = AsyncMock(return_value=_mock_result(value=None))

    svc = AuthService(db)
    await svc.forgot_password("noone@test.com")  # Should not raise


@pytest.mark.asyncio
async def test_auth_reset_password_expired():
    from app.services.auth import AuthService, TokenInvalidError

    db = _mock_db()
    token_record = MagicMock()
    token_record.used_at = None
    token_record.expires_at = datetime.now(UTC) - timedelta(hours=2)
    db.execute = AsyncMock(return_value=_mock_result(value=token_record))

    svc = AuthService(db)
    with pytest.raises(TokenInvalidError, match="expired"):
        await svc.reset_password("expired-token", "NewPass123!")


@pytest.mark.asyncio
async def test_auth_reset_password_already_used():
    from app.services.auth import AuthService, TokenInvalidError

    db = _mock_db()
    token_record = MagicMock()
    token_record.used_at = datetime.now(UTC)
    db.execute = AsyncMock(return_value=_mock_result(value=token_record))

    svc = AuthService(db)
    with pytest.raises(TokenInvalidError, match="already used"):
        await svc.reset_password("used-token", "NewPass123!")


@pytest.mark.asyncio
async def test_auth_verify_email_not_found():
    from app.services.auth import AuthService, TokenInvalidError

    db = _mock_db()
    db.execute = AsyncMock(return_value=_mock_result(value=None))

    svc = AuthService(db)
    with pytest.raises(TokenInvalidError, match="Invalid verification"):
        await svc.verify_email("bad-token")


@pytest.mark.asyncio
async def test_auth_resend_already_verified():
    from app.services.auth import AuthService

    db = _mock_db()
    user = MagicMock()
    user.email_verified = True

    svc = AuthService(db)
    await svc.resend_verification(user)  # Should return immediately


# ── OrgService ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_org_add_member_already_active():
    from app.models.organization import MemberStatus
    from app.services.organization import AlreadyMemberError, OrgService

    db = _mock_db()
    existing = MagicMock()
    existing.status = MemberStatus.ACTIVE
    db.execute = AsyncMock(return_value=_mock_result(value=existing))

    svc = OrgService(db)
    with pytest.raises(AlreadyMemberError):
        await svc.add_member("org1", "user1", MagicMock())


@pytest.mark.asyncio
async def test_org_remove_owner():
    from app.models.organization import MemberStatus, OrgRole
    from app.services.organization import CannotRemoveOwnerError, OrgService

    db = _mock_db()
    member = MagicMock()
    member.role = OrgRole.OWNER
    member.status = MemberStatus.ACTIVE
    db.execute = AsyncMock(return_value=_mock_result(value=member))

    svc = OrgService(db)
    with pytest.raises(CannotRemoveOwnerError):
        await svc.remove_member("org1", "owner1", "admin1")


@pytest.mark.asyncio
async def test_org_delete_not_owner():
    from app.models.organization import MemberStatus, OrgRole
    from app.services.organization import InsufficientOrgPermissionError, OrgService

    db = _mock_db()
    org = MagicMock()
    member = MagicMock()
    member.role = OrgRole.ADMIN
    member.status = MemberStatus.ACTIVE

    db.get = AsyncMock(return_value=org)
    db.execute = AsyncMock(return_value=_mock_result(value=member))

    svc = OrgService(db)
    with pytest.raises(InsufficientOrgPermissionError):
        await svc.delete_org("org1", "admin1")


@pytest.mark.asyncio
async def test_org_slug_already_exists():
    from app.services.organization import OrgService, SlugAlreadyExistsError

    db = _mock_db()
    db.execute = AsyncMock(return_value=_mock_result(value=MagicMock()))  # slug exists

    svc = OrgService(db)
    with pytest.raises(SlugAlreadyExistsError):
        await svc.create("Test", "taken-slug", None, "user1")


@pytest.mark.asyncio
async def test_org_invite_link_expired():
    from app.services.organization import InviteLinkInvalidError, OrgService

    db = _mock_db()
    link = MagicMock()
    link.is_active = True
    link.expires_at = datetime.now(UTC) - timedelta(days=1)
    link.max_uses = None
    db.execute = AsyncMock(return_value=_mock_result(value=link))

    svc = OrgService(db)
    with pytest.raises(InviteLinkInvalidError, match="expired"):
        await svc.join_by_code("abc", "user1")


@pytest.mark.asyncio
async def test_org_invite_link_max_uses():
    from app.services.organization import InviteLinkInvalidError, OrgService

    db = _mock_db()
    link = MagicMock()
    link.is_active = True
    link.expires_at = None
    link.max_uses = 5
    link.use_count = 5
    db.execute = AsyncMock(return_value=_mock_result(value=link))

    svc = OrgService(db)
    with pytest.raises(InviteLinkInvalidError, match="maximum"):
        await svc.join_by_code("abc", "user1")


# ── SkillService ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_skill_locked():
    from app.services.skill import SkillLockedError, SkillService

    db = _mock_db()
    svc = SkillService(db)
    svc.get_exercise = AsyncMock(return_value=MagicMock(skill_id="s1"))
    svc.is_skill_unlocked = AsyncMock(return_value=False)

    with pytest.raises(SkillLockedError):
        await svc.submit_attempt("org1", "ex1", "user1", {"selected": ["a"]})


@pytest.mark.asyncio
async def test_skill_not_found():
    from app.services.skill import SkillNotFoundError, SkillService

    db = _mock_db()
    db.get = AsyncMock(return_value=None)

    svc = SkillService(db)
    with pytest.raises(SkillNotFoundError):
        await svc.get_skill("nonexistent")


@pytest.mark.asyncio
async def test_exercise_not_found():
    from app.services.skill import ExerciseNotFoundError, SkillService

    db = _mock_db()
    db.get = AsyncMock(return_value=None)

    svc = SkillService(db)
    with pytest.raises(ExerciseNotFoundError):
        await svc.get_exercise("nonexistent")


@pytest.mark.asyncio
async def test_category_not_found():
    from app.services.skill import CategoryNotFoundError, SkillService

    db = _mock_db()
    db.get = AsyncMock(return_value=None)

    svc = SkillService(db)
    with pytest.raises(CategoryNotFoundError):
        await svc.get_category("nonexistent")


# ── ProjectService ───────────────────────────────────────


@pytest.mark.asyncio
async def test_project_not_found():
    from app.services.project import ProjectNotFoundError, ProjectService

    db = _mock_db()
    db.get = AsyncMock(return_value=None)

    svc = ProjectService(db)
    with pytest.raises(ProjectNotFoundError):
        await svc.get_project("nonexistent")


@pytest.mark.asyncio
async def test_submission_not_found():
    from app.services.project import ProjectService, SubmissionNotFoundError

    db = _mock_db()
    db.get = AsyncMock(return_value=None)

    svc = ProjectService(db)
    with pytest.raises(SubmissionNotFoundError):
        await svc.get_submission("nonexistent")


@pytest.mark.asyncio
async def test_submit_not_owner():
    from app.exceptions import AppError
    from app.services.project import ProjectService

    db = _mock_db()
    sub = MagicMock()
    sub.user_id = "other-user"
    db.get = AsyncMock(return_value=sub)

    svc = ProjectService(db)
    with pytest.raises(AppError, match="Not your submission"):
        await svc.submit_draft("sub1", "my-user")


@pytest.mark.asyncio
async def test_submit_not_draft():
    from app.models.project import SubmissionStatus
    from app.services.project import InvalidStateError, ProjectService

    db = _mock_db()
    sub = MagicMock()
    sub.user_id = "user1"
    sub.status = SubmissionStatus.SUBMITTED
    db.get = AsyncMock(return_value=sub)

    svc = ProjectService(db)
    with pytest.raises(InvalidStateError):
        await svc.submit_draft("sub1", "user1")


@pytest.mark.asyncio
async def test_max_submissions_reached():
    from app.models.skill import ContentStatus
    from app.services.project import MaxSubmissionsReachedError, ProjectService

    db = _mock_db()
    project = MagicMock()
    project.max_submissions = 2
    project.status = ContentStatus.PUBLISHED
    project.org_id = "org1"

    # The first db.execute call returns the project (SELECT ... FOR UPDATE),
    # subsequent calls return None (no cohort/creator assignments) or count=2.
    call_count = 0

    async def _mock_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Project query
            return _mock_result(value=project)
        elif call_count <= 3:
            # Cohort/creator assignment checks — no assignments
            return _mock_result(value=None)
        else:
            # Submission count
            return _mock_result(value=2)

    db.execute = _mock_execute

    svc = ProjectService(db)
    with pytest.raises(MaxSubmissionsReachedError):
        await svc.create_submission("org1", "proj1", "user1")


@pytest.mark.asyncio
async def test_file_too_large():
    from app.models.project import SubmissionStatus
    from app.services.project import FileTooLargeError, ProjectService

    db = _mock_db()
    sub = MagicMock()
    sub.user_id = "user1"
    sub.status = SubmissionStatus.DRAFT
    sub.org_id = "org1"
    db.get = AsyncMock(return_value=sub)

    svc = ProjectService(db)
    big_content = b"x" * (51 * 1024 * 1024)
    with pytest.raises(FileTooLargeError):
        await svc.upload_file(
            "sub1", "del1", "big.bin", big_content, "application/octet-stream", "user1"
        )


# ── EvaluationService ────────────────────────────────────


@pytest.mark.asyncio
async def test_eval_budget_exceeded():
    from app.services.evaluation import BudgetExceededError, EvaluationService

    db = _mock_db()
    # trigger_evaluation now validates the submission belongs to the org before
    # checking budget — return a matching submission so we reach the budget path.
    submission = MagicMock()
    submission.org_id = "org1"
    db.get = AsyncMock(return_value=submission)
    svc = EvaluationService(db)
    # enabled gate now runs before the budget check
    svc.get_eval_settings = AsyncMock(return_value={"enabled": True})
    svc.check_budget = AsyncMock(return_value=False)

    with pytest.raises(BudgetExceededError):
        await svc.trigger_evaluation("org1", "sub1", "submission_review")


@pytest.mark.asyncio
async def test_eval_task_not_found():
    from app.services.evaluation import EvalTaskNotFoundError, EvaluationService

    db = _mock_db()
    db.get = AsyncMock(return_value=None)

    svc = EvaluationService(db)
    with pytest.raises(EvalTaskNotFoundError):
        await svc.get_task("nonexistent")


@pytest.mark.asyncio
async def test_eval_cancel_not_pending():
    from app.exceptions import AppError
    from app.models.evaluation import EvalStatus
    from app.services.evaluation import EvaluationService

    db = _mock_db()
    task = MagicMock()
    task.status = EvalStatus.COMPLETED
    db.get = AsyncMock(return_value=task)

    svc = EvaluationService(db)
    with pytest.raises(AppError, match="Only pending"):
        await svc.cancel_task("task1")


@pytest.mark.asyncio
async def test_eval_retry_not_failed():
    from app.exceptions import AppError
    from app.models.evaluation import EvalStatus
    from app.services.evaluation import EvaluationService

    db = _mock_db()
    task = MagicMock()
    task.status = EvalStatus.PENDING
    db.get = AsyncMock(return_value=task)

    svc = EvaluationService(db)
    with pytest.raises(AppError, match="Only failed"):
        await svc.retry_task("task1")


# ── PortfolioService ─────────────────────────────────────


@pytest.mark.asyncio
async def test_portfolio_item_not_found():
    from app.services.portfolio import ItemNotFoundError, PortfolioService

    db = _mock_db()
    db.get = AsyncMock(return_value=None)

    svc = PortfolioService(db)
    with pytest.raises(ItemNotFoundError):
        await svc.get_item("nonexistent")


@pytest.mark.asyncio
async def test_portfolio_update_not_owner():
    from app.exceptions import AppError
    from app.services.portfolio import PortfolioService

    db = _mock_db()
    item = MagicMock()
    item.user_id = "other-user"
    db.get = AsyncMock(return_value=item)

    svc = PortfolioService(db)
    with pytest.raises(AppError, match="Not your item"):
        await svc.update_item("item1", "my-user", title="New")


@pytest.mark.asyncio
async def test_portfolio_delete_not_owner():
    from app.exceptions import AppError
    from app.services.portfolio import PortfolioService

    db = _mock_db()
    item = MagicMock()
    item.user_id = "other-user"
    db.get = AsyncMock(return_value=item)

    svc = PortfolioService(db)
    with pytest.raises(AppError, match="Not your item"):
        await svc.delete_item("item1", "my-user")


@pytest.mark.asyncio
async def test_portfolio_username_taken():
    from app.services.portfolio import PortfolioService, UsernameUnavailableError

    db = _mock_db()
    # First call: uniqueness check returns existing profile
    existing_profile = MagicMock()
    existing_profile.user_id = "other-user"
    db.execute = AsyncMock(return_value=_mock_result(value=existing_profile))

    svc = PortfolioService(db)
    with pytest.raises(UsernameUnavailableError):
        await svc.set_username("my-user", "taken-name")


@pytest.mark.asyncio
async def test_portfolio_profile_not_found():
    from app.services.portfolio import PortfolioService

    db = _mock_db()
    db.execute = AsyncMock(return_value=_mock_result(value=None))

    svc = PortfolioService(db)
    result = await svc.get_public_profile("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_eval_parse_tolerates_hostile_score_types():
    """A hallucinated LLM score (string/null/list) raised TypeError in
    min() and failed the whole paid evaluation (bug #138). Non-numeric
    scores now degrade to 0 instead of crashing."""
    from app.services.evaluation import EvaluationService

    svc = EvaluationService.__new__(EvaluationService)
    rubric = [{"criterion": "Quality", "max_score": 100}]
    for bad in (
        '{"scores":[{"criterion":"Quality","score":"high"}]}',
        '{"scores":[{"criterion":"Quality","score":null}]}',
        '{"scores":[{"criterion":"Quality","score":[1,2]}]}',
    ):
        r = svc._parse_evaluation_response(bad, rubric)
        assert r["total_score"] == 0
        assert r["scores"][0]["score"] == 0
    # a valid score still works and clamps to max
    r = svc._parse_evaluation_response('{"scores":[{"criterion":"Quality","score":150}]}', rubric)
    assert r["scores"][0]["score"] == 100
