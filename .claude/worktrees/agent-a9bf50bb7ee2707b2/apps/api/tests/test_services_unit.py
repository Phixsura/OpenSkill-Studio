"""Comprehensive service unit tests using mocked DB sessions."""

import pytest
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from unittest.mock import AsyncMock, MagicMock, patch


def make_db():
    """Create a mock async DB session."""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    return db


def mock_execute_returns(value):
    """Helper: db.execute returns a result with scalar_one_or_none = value."""
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=value)
    result.scalar_one = MagicMock(return_value=value if value is not None else 0)
    result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    return result


# ── AuthService ──────────────────────────────────────────────


class TestAuthService:
    @pytest.mark.asyncio
    async def test_register_success(self):
        from app.services.auth import AuthService

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(None))  # No existing user
        db.get = AsyncMock(return_value=None)

        svc = AuthService(db)
        with patch("app.services.auth.get_email_sender") as mock_sender:
            mock_sender.return_value = AsyncMock()
            mock_sender.return_value.send = AsyncMock()
            result = await svc.register("test@example.com", "StrongPass1!", "Test User")

        assert result.access_token is not None
        assert result.user is not None
        db.add.assert_called()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        from app.services.auth import AuthService, EmailAlreadyExistsError

        db = make_db()
        existing_user = MagicMock()
        db.execute = AsyncMock(return_value=mock_execute_returns(existing_user))

        svc = AuthService(db)
        with pytest.raises(EmailAlreadyExistsError):
            await svc.register("taken@example.com", "StrongPass1!", "Test")

    @pytest.mark.asyncio
    async def test_login_success(self):
        from app.models.user import User, UserRole, UserStatus
        from app.services.auth import AuthService

        db = make_db()
        user = MagicMock(spec=User)
        user.id = "01USER"
        user.email = "test@example.com"
        user.has_password = True
        user.password_hash = "$2b$12$test"
        user.status = UserStatus.ACTIVE
        user.role = UserRole.STUDENT
        user.is_active = True

        db.execute = AsyncMock(return_value=mock_execute_returns(user))

        svc = AuthService(db)
        with patch("app.services.auth.verify_password", return_value=True):
            result = await svc.login("test@example.com", "password")

        assert result.access_token is not None

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        from app.models.user import User, UserStatus
        from app.services.auth import AuthService, InvalidCredentialsError

        db = make_db()
        user = MagicMock(spec=User)
        user.has_password = True
        user.password_hash = "$2b$12$test"
        user.status = UserStatus.ACTIVE

        db.execute = AsyncMock(return_value=mock_execute_returns(user))

        svc = AuthService(db)
        with patch("app.services.auth.verify_password", return_value=False):
            with pytest.raises(InvalidCredentialsError):
                await svc.login("test@example.com", "wrong")

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        from app.services.auth import AuthService, InvalidCredentialsError

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(None))

        svc = AuthService(db)
        with pytest.raises(InvalidCredentialsError):
            await svc.login("nobody@example.com", "pass")

    @pytest.mark.asyncio
    async def test_login_suspended_user(self):
        from app.models.user import User, UserStatus
        from app.services.auth import AccountSuspendedError, AuthService

        db = make_db()
        user = MagicMock(spec=User)
        user.has_password = True
        user.password_hash = "hash"
        user.status = UserStatus.SUSPENDED

        db.execute = AsyncMock(return_value=mock_execute_returns(user))

        svc = AuthService(db)
        with patch("app.services.auth.verify_password", return_value=True):
            with pytest.raises(AccountSuspendedError):
                await svc.login("test@example.com", "pass")

    @pytest.mark.asyncio
    async def test_login_deleted_user(self):
        from app.models.user import User, UserStatus
        from app.services.auth import AuthService, InvalidCredentialsError

        db = make_db()
        user = MagicMock(spec=User)
        user.has_password = True
        user.password_hash = "hash"
        user.status = UserStatus.DELETED

        db.execute = AsyncMock(return_value=mock_execute_returns(user))

        svc = AuthService(db)
        with patch("app.services.auth.verify_password", return_value=True):
            with pytest.raises(InvalidCredentialsError):
                await svc.login("test@example.com", "pass")

    @pytest.mark.asyncio
    async def test_logout(self):
        from app.core.security import create_refresh_token
        from app.services.auth import AuthService

        db = make_db()
        token, jti, _ = create_refresh_token("user1")

        mock_record = MagicMock()
        mock_record.is_revoked = False
        db.execute = AsyncMock(return_value=mock_execute_returns(mock_record))

        svc = AuthService(db)
        await svc.logout(token)
        # Should not raise

    @pytest.mark.asyncio
    async def test_logout_invalid_token(self):
        from app.services.auth import AuthService

        db = make_db()
        svc = AuthService(db)
        await svc.logout("invalid-token")
        # Should not raise, silently ignore

    @pytest.mark.asyncio
    async def test_change_password_success(self):
        from app.models.user import User
        from app.services.auth import AuthService

        db = make_db()
        user = MagicMock(spec=User)
        user.id = "01USER"
        user.has_password = True
        user.password_hash = "old_hash"

        result_mock = MagicMock()
        result_mock.scalars = MagicMock(return_value=iter([]))
        db.execute = AsyncMock(return_value=result_mock)

        svc = AuthService(db)
        with patch("app.services.auth.verify_password", return_value=True):
            await svc.change_password(user, "oldpass", "NewPass123!")

    @pytest.mark.asyncio
    async def test_change_password_wrong_old(self):
        from app.models.user import User
        from app.services.auth import AuthService, InvalidCredentialsError

        db = make_db()
        user = MagicMock(spec=User)
        user.has_password = True
        user.password_hash = "hash"

        svc = AuthService(db)
        with patch("app.services.auth.verify_password", return_value=False):
            with pytest.raises(InvalidCredentialsError):
                await svc.change_password(user, "wrong", "NewPass123!")

    @pytest.mark.asyncio
    async def test_forgot_password_user_not_found(self):
        from app.services.auth import AuthService

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(None))

        svc = AuthService(db)
        await svc.forgot_password("nobody@test.com")
        # Should silently succeed (no user enumeration)

    @pytest.mark.asyncio
    async def test_forgot_password_sends_email(self):
        from app.models.user import User
        from app.services.auth import AuthService

        db = make_db()
        user = MagicMock(spec=User)
        user.id = "01USER"
        user.email = "test@example.com"

        # First call: find user, second call: find existing reset tokens
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_execute_returns(user)
            result = MagicMock()
            result.scalars = MagicMock(return_value=iter([]))
            return result

        db.execute = AsyncMock(side_effect=side_effect)

        svc = AuthService(db)
        with patch("app.services.auth.get_email_sender") as mock_sender:
            mock_sender.return_value = AsyncMock()
            mock_sender.return_value.send = AsyncMock()
            await svc.forgot_password("test@example.com")
            mock_sender.return_value.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(self):
        from app.services.auth import AuthService, TokenInvalidError

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(None))

        svc = AuthService(db)
        with pytest.raises(TokenInvalidError, match="Invalid reset"):
            await svc.reset_password("bad-token", "NewPass123!")

    @pytest.mark.asyncio
    async def test_reset_password_expired(self):
        from app.services.auth import AuthService, TokenInvalidError

        db = make_db()
        token_record = MagicMock()
        token_record.used_at = None
        token_record.expires_at = datetime.now(UTC) - timedelta(hours=2)
        db.execute = AsyncMock(return_value=mock_execute_returns(token_record))

        svc = AuthService(db)
        with pytest.raises(TokenInvalidError, match="expired"):
            await svc.reset_password("token", "NewPass123!")

    @pytest.mark.asyncio
    async def test_reset_password_already_used(self):
        from app.services.auth import AuthService, TokenInvalidError

        db = make_db()
        token_record = MagicMock()
        token_record.used_at = datetime.now(UTC)
        db.execute = AsyncMock(return_value=mock_execute_returns(token_record))

        svc = AuthService(db)
        with pytest.raises(TokenInvalidError, match="already used"):
            await svc.reset_password("token", "NewPass123!")

    @pytest.mark.asyncio
    async def test_verify_email_invalid(self):
        from app.services.auth import AuthService, TokenInvalidError

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(None))

        svc = AuthService(db)
        with pytest.raises(TokenInvalidError, match="Invalid verification"):
            await svc.verify_email("bad-token")

    @pytest.mark.asyncio
    async def test_resend_verification_already_verified(self):
        from app.models.user import User
        from app.services.auth import AuthService

        db = make_db()
        user = MagicMock(spec=User)
        user.email_verified = True

        svc = AuthService(db)
        await svc.resend_verification(user)
        # Should return early without creating a new token

    @pytest.mark.asyncio
    async def test_list_sessions(self):
        from app.services.auth import AuthService

        db = make_db()
        result = MagicMock()
        result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        db.execute = AsyncMock(return_value=result)

        svc = AuthService(db)
        sessions = await svc.list_sessions("user1")
        assert sessions == []

    @pytest.mark.asyncio
    async def test_revoke_session_not_found(self):
        from app.exceptions import AppError
        from app.services.auth import AuthService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = AuthService(db)
        with pytest.raises(AppError, match="NOT_FOUND"):
            await svc.revoke_session("user1", "bad-id")


# ── OrgService ───────────────────────────────────────────────


class TestOrgService:
    @pytest.mark.asyncio
    async def test_create_org(self):
        from app.services.organization import OrgService

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(None))  # Slug available

        svc = OrgService(db)
        org = await svc.create("Test Org", "test-org", None, "user1")
        assert org is not None
        assert db.add.call_count >= 2  # org + member

    @pytest.mark.asyncio
    async def test_create_org_duplicate_slug(self):
        from app.services.organization import OrgService, SlugAlreadyExistsError

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(MagicMock()))  # Slug taken

        svc = OrgService(db)
        with pytest.raises(SlugAlreadyExistsError):
            await svc.create("Test", "taken-slug", None, "user1")

    @pytest.mark.asyncio
    async def test_get_org_not_found(self):
        from app.services.organization import OrgNotFoundError, OrgService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = OrgService(db)
        with pytest.raises(OrgNotFoundError):
            await svc.get_org("bad-id")

    @pytest.mark.asyncio
    async def test_delete_org_not_owner(self):
        from app.models.organization import MemberStatus, OrgMember, OrgRole
        from app.services.organization import InsufficientOrgPermissionError, OrgService

        db = make_db()
        org = MagicMock()
        db.get = AsyncMock(return_value=org)

        member = MagicMock(spec=OrgMember)
        member.role = OrgRole.ADMIN
        member.status = MemberStatus.ACTIVE
        db.execute = AsyncMock(return_value=mock_execute_returns(member))

        svc = OrgService(db)
        with pytest.raises(InsufficientOrgPermissionError):
            await svc.delete_org("org1", "user1")

    @pytest.mark.asyncio
    async def test_add_member_already_exists(self):
        from app.models.organization import MemberStatus, OrgMember
        from app.services.organization import AlreadyMemberError, OrgService

        db = make_db()
        existing = MagicMock(spec=OrgMember)
        existing.status = MemberStatus.ACTIVE
        db.execute = AsyncMock(return_value=mock_execute_returns(existing))

        svc = OrgService(db)
        with pytest.raises(AlreadyMemberError):
            from app.models.organization import OrgRole

            await svc.add_member("org1", "user1", OrgRole.STUDENT)

    @pytest.mark.asyncio
    async def test_add_member_reactivate_archived(self):
        from app.models.organization import MemberStatus, OrgMember, OrgRole
        from app.services.organization import OrgService

        db = make_db()
        existing = MagicMock(spec=OrgMember)
        existing.status = MemberStatus.ARCHIVED
        db.execute = AsyncMock(return_value=mock_execute_returns(existing))

        svc = OrgService(db)
        result = await svc.add_member("org1", "user1", OrgRole.STUDENT)
        assert result.status == MemberStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_remove_member_cannot_remove_owner(self):
        from app.models.organization import MemberStatus, OrgMember, OrgRole
        from app.services.organization import CannotRemoveOwnerError, OrgService

        db = make_db()
        owner = MagicMock(spec=OrgMember)
        owner.role = OrgRole.OWNER
        owner.status = MemberStatus.ACTIVE
        db.execute = AsyncMock(return_value=mock_execute_returns(owner))

        svc = OrgService(db)
        with pytest.raises(CannotRemoveOwnerError):
            await svc.remove_member("org1", "owner-id", "admin-id")

    def test_generate_slug(self):
        from app.services.organization import OrgService

        assert OrgService._generate_slug("Hello World") == "hello-world"
        assert len(OrgService._generate_slug("AB")) >= 3
        assert OrgService._generate_slug("Phixsura Academy") == "phixsura-academy"

    def test_can_manage_member(self):
        from app.models.organization import OrgRole
        from app.services.organization import OrgService

        svc = OrgService.__new__(OrgService)

        def m(role):
            mock = MagicMock()
            mock.role = role
            return mock

        assert svc._can_manage_member(m(OrgRole.OWNER), m(OrgRole.ADMIN))
        assert not svc._can_manage_member(m(OrgRole.STUDENT), m(OrgRole.STUDENT))
        assert not svc._can_manage_member(m(OrgRole.ADMIN), m(OrgRole.OWNER))


# ── SkillService ─────────────────────────────────────────────


class TestSkillService:
    @pytest.mark.asyncio
    async def test_create_category(self):
        from app.services.skill import SkillService

        db = make_db()
        svc = SkillService(db)
        cat = await svc.create_category("org1", "AI", None, None, None, "user1")
        assert cat is not None
        db.add.assert_called()

    @pytest.mark.asyncio
    async def test_create_skill(self):
        from app.services.skill import SkillService

        db = make_db()
        svc = SkillService(db)
        skill = await svc.create_skill(
            "org1", "cat1", "Python", None, "Learn Python",
            None, "beginner", None, None, None, "user1",
        )
        assert skill is not None

    @pytest.mark.asyncio
    async def test_publish_skill(self):
        from app.models.skill import ContentStatus
        from app.services.skill import SkillService

        db = make_db()
        skill = MagicMock()
        skill.status = ContentStatus.DRAFT
        db.get = AsyncMock(return_value=skill)

        svc = SkillService(db)
        result = await svc.publish_skill("skill1")
        assert result.status == ContentStatus.PUBLISHED

    @pytest.mark.asyncio
    async def test_unpublish_skill(self):
        from app.models.skill import ContentStatus
        from app.services.skill import SkillService

        db = make_db()
        skill = MagicMock()
        skill.status = ContentStatus.PUBLISHED
        db.get = AsyncMock(return_value=skill)

        svc = SkillService(db)
        result = await svc.unpublish_skill("skill1")
        assert result.status == ContentStatus.DRAFT

    @pytest.mark.asyncio
    async def test_skill_not_found(self):
        from app.services.skill import SkillNotFoundError, SkillService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = SkillService(db)
        with pytest.raises(SkillNotFoundError):
            await svc.get_skill("bad-id")

    @pytest.mark.asyncio
    async def test_exercise_not_found(self):
        from app.services.skill import ExerciseNotFoundError, SkillService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = SkillService(db)
        with pytest.raises(ExerciseNotFoundError):
            await svc.get_exercise("bad-id")

    @pytest.mark.asyncio
    async def test_attempt_not_found(self):
        from app.services.skill import AttemptNotFoundError, SkillService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = SkillService(db)
        with pytest.raises(AttemptNotFoundError):
            await svc.grade_attempt("bad-id", 80, "good")

    @pytest.mark.asyncio
    async def test_is_skill_unlocked_no_prereqs(self):
        from app.services.skill import SkillService

        db = make_db()
        result = MagicMock()
        result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        db.execute = AsyncMock(return_value=result)

        svc = SkillService(db)
        unlocked = await svc.is_skill_unlocked("skill1", "user1")
        assert unlocked is True

    def test_skill_slug_generation(self):
        from app.services.skill import SkillService

        assert SkillService._generate_slug("Few-Shot Prompting") == "few-shot-prompting"
        assert len(SkillService._generate_slug("AB")) >= 3


# ── ProjectService ───────────────────────────────────────────


class TestProjectService:
    @pytest.mark.asyncio
    async def test_create_project(self):
        from app.services.project import ProjectService

        db = make_db()
        svc = ProjectService(db)
        project = await svc.create_project(
            "org1", "Test Project", None, "Description", "Instructions",
            "intermediate", 100, [{"criterion": "X", "max_score": 50}],
            None, None, 0, 0, None, "user1",
        )
        assert project is not None

    @pytest.mark.asyncio
    async def test_project_not_found(self):
        from app.services.project import ProjectNotFoundError, ProjectService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = ProjectService(db)
        with pytest.raises(ProjectNotFoundError):
            await svc.get_project("bad-id")

    @pytest.mark.asyncio
    async def test_submission_not_found(self):
        from app.services.project import ProjectService, SubmissionNotFoundError

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = ProjectService(db)
        with pytest.raises(SubmissionNotFoundError):
            await svc.get_submission("bad-id")

    @pytest.mark.asyncio
    async def test_max_submissions_reached(self):
        from app.services.project import MaxSubmissionsReachedError, ProjectService

        db = make_db()
        project = MagicMock()
        project.max_submissions = 2
        db.get = AsyncMock(return_value=project)
        db.execute = AsyncMock(return_value=mock_execute_returns(2))  # Already 2 submissions

        svc = ProjectService(db)
        with pytest.raises(MaxSubmissionsReachedError):
            await svc.create_submission("org1", "proj1", "user1")

    @pytest.mark.asyncio
    async def test_file_too_large(self):
        from app.services.project import FileTooLargeError, ProjectService

        db = make_db()
        sub = MagicMock()
        sub.user_id = "user1"
        sub.status = MagicMock(value="draft")
        sub.org_id = "org1"
        db.get = AsyncMock(return_value=sub)

        svc = ProjectService(db)
        large_content = b"x" * (51 * 1024 * 1024)
        with pytest.raises(FileTooLargeError):
            await svc.upload_file("sub1", "del1", "test.py", large_content, "text/python", "user1")

    def test_calculate_final_score_no_penalty(self):
        from app.services.project import ProjectService

        project = MagicMock()
        project.late_penalty_pct = 20
        assert ProjectService._calculate_final_score(100, is_late=False, project=project) == 100

    def test_calculate_final_score_with_penalty(self):
        from app.services.project import ProjectService

        project = MagicMock()
        project.late_penalty_pct = 20
        assert ProjectService._calculate_final_score(100, is_late=True, project=project) == 80

    def test_calculate_final_score_zero_penalty(self):
        from app.services.project import ProjectService

        project = MagicMock()
        project.late_penalty_pct = 0
        assert ProjectService._calculate_final_score(100, is_late=True, project=project) == 100

    def test_project_slug_generation(self):
        from app.services.project import ProjectService

        assert ProjectService._generate_slug("AI Chatbot") == "ai-chatbot"

    @pytest.mark.asyncio
    async def test_deliverable_not_found(self):
        from app.services.project import DeliverableNotFoundError, ProjectService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = ProjectService(db)
        with pytest.raises(DeliverableNotFoundError):
            await svc.update_deliverable("bad-id")

    @pytest.mark.asyncio
    async def test_delete_deliverable_not_found(self):
        from app.services.project import DeliverableNotFoundError, ProjectService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = ProjectService(db)
        with pytest.raises(DeliverableNotFoundError):
            await svc.delete_deliverable("bad-id")


# ── EvaluationService ────────────────────────────────────────


class TestEvaluationService:
    @pytest.mark.asyncio
    async def test_check_budget_no_limit(self):
        from app.services.evaluation import EvaluationService

        db = make_db()
        org = MagicMock()
        org.settings = {}
        db.get = AsyncMock(return_value=org)

        svc = EvaluationService(db)
        assert await svc.check_budget("org1") is True

    @pytest.mark.asyncio
    async def test_check_budget_under_limit(self):
        from app.services.evaluation import EvaluationService

        db = make_db()
        org = MagicMock()
        org.settings = {"ai_evaluation": {"monthly_budget_usd": 100.0}}
        db.get = AsyncMock(return_value=org)
        db.execute = AsyncMock(return_value=mock_execute_returns(None))

        svc = EvaluationService(db)
        assert await svc.check_budget("org1") is True

    @pytest.mark.asyncio
    async def test_check_budget_exceeded(self):
        from app.services.evaluation import EvaluationService

        db = make_db()
        org = MagicMock()
        org.settings = {"ai_evaluation": {"monthly_budget_usd": 10.0}}
        db.get = AsyncMock(return_value=org)

        usage = MagicMock()
        usage.total_cost_usd = Decimal("15.0")
        db.execute = AsyncMock(return_value=mock_execute_returns(usage))

        svc = EvaluationService(db)
        assert await svc.check_budget("org1") is False

    @pytest.mark.asyncio
    async def test_get_eval_settings_defaults(self):
        from app.services.evaluation import EvaluationService

        db = make_db()
        org = MagicMock()
        org.settings = {}
        db.get = AsyncMock(return_value=org)

        svc = EvaluationService(db)
        settings = await svc.get_eval_settings("org1")
        assert settings["enabled"] is False
        assert settings["pass_threshold"] == 0.6

    @pytest.mark.asyncio
    async def test_get_eval_settings_custom(self):
        from app.services.evaluation import EvaluationService

        db = make_db()
        org = MagicMock()
        org.settings = {"ai_evaluation": {"enabled": True, "monthly_budget_usd": 50.0}}
        db.get = AsyncMock(return_value=org)

        svc = EvaluationService(db)
        settings = await svc.get_eval_settings("org1")
        assert settings["enabled"] is True
        assert settings["monthly_budget_usd"] == 50.0

    @pytest.mark.asyncio
    async def test_update_eval_settings(self):
        from app.services.evaluation import EvaluationService

        db = make_db()
        org = MagicMock()
        org.settings = {}
        db.get = AsyncMock(return_value=org)

        svc = EvaluationService(db)
        result = await svc.update_eval_settings("org1", {"enabled": True})
        assert result["enabled"] is True

    @pytest.mark.asyncio
    async def test_get_usage_empty(self):
        from app.services.evaluation import EvaluationService

        db = make_db()
        org = MagicMock()
        org.settings = {}
        db.get = AsyncMock(return_value=org)
        db.execute = AsyncMock(return_value=mock_execute_returns(None))

        svc = EvaluationService(db)
        usage = await svc.get_usage("org1")
        assert usage["total_tasks"] == 0

    @pytest.mark.asyncio
    async def test_cancel_task_not_pending(self):
        from app.exceptions import AppError
        from app.models.evaluation import EvalStatus
        from app.services.evaluation import EvaluationService

        db = make_db()
        task = MagicMock()
        task.status = EvalStatus.COMPLETED
        db.get = AsyncMock(return_value=task)

        svc = EvaluationService(db)
        with pytest.raises(AppError, match="INVALID_STATE"):
            await svc.cancel_task("task1")

    @pytest.mark.asyncio
    async def test_retry_task_not_failed(self):
        from app.exceptions import AppError
        from app.models.evaluation import EvalStatus
        from app.services.evaluation import EvaluationService

        db = make_db()
        task = MagicMock()
        task.status = EvalStatus.PENDING
        db.get = AsyncMock(return_value=task)

        svc = EvaluationService(db)
        with pytest.raises(AppError, match="INVALID_STATE"):
            await svc.retry_task("task1")

    @pytest.mark.asyncio
    async def test_task_not_found(self):
        from app.services.evaluation import EvalTaskNotFoundError, EvaluationService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = EvaluationService(db)
        with pytest.raises(EvalTaskNotFoundError):
            await svc.get_task("bad-id")

    def test_format_rubric(self):
        from app.services.evaluation import EvaluationService

        rubric = [
            {"criterion": "Quality", "max_score": 50, "description": "Good code"},
            {"criterion": "Design", "max_score": 30},
        ]
        result = EvaluationService._format_rubric(rubric)
        assert "Quality" in result
        assert "0-50 points" in result

    def test_format_rubric_dict_input(self):
        from app.services.evaluation import EvaluationService

        rubric = {"rubric": [{"criterion": "X", "max_score": 10}]}
        result = EvaluationService._format_rubric(rubric)
        assert "X" in result

    def test_format_submission_empty(self):
        from app.services.evaluation import EvaluationService

        result = EvaluationService._format_submission([])
        assert "No content" in result

    def test_format_submission_mixed(self):
        from app.services.evaluation import EvaluationService

        item1 = MagicMock()
        item1.content = "Answer text"
        item1.file_name = None
        item2 = MagicMock()
        item2.content = None
        item2.file_name = "code.py"

        result = EvaluationService._format_submission([item1, item2])
        assert "Answer text" in result
        assert "[File: code.py]" in result


# ── PortfolioService ─────────────────────────────────────────


class TestPortfolioService:
    @pytest.mark.asyncio
    async def test_get_or_create_profile_existing(self):
        from app.services.portfolio import PortfolioService

        db = make_db()
        profile = MagicMock()
        db.get = AsyncMock(return_value=profile)

        svc = PortfolioService(db)
        result = await svc.get_or_create_profile("user1")
        assert result is profile

    @pytest.mark.asyncio
    async def test_get_or_create_profile_new(self):
        from app.models.user import User
        from app.services.portfolio import PortfolioService

        db = make_db()
        user = MagicMock(spec=User)
        user.display_name = "Alice Wang"

        # First get returns None (no profile), second returns user
        db.get = AsyncMock(side_effect=[None, user])
        db.execute = AsyncMock(return_value=mock_execute_returns(None))  # Username available

        svc = PortfolioService(db)
        result = await svc.get_or_create_profile("user1")
        assert result is not None
        db.add.assert_called()

    @pytest.mark.asyncio
    async def test_set_username_taken(self):
        from app.services.portfolio import PortfolioService, UsernameUnavailableError

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(MagicMock()))  # Username taken
        db.get = AsyncMock(return_value=MagicMock())

        svc = PortfolioService(db)
        with pytest.raises(UsernameUnavailableError):
            await svc.set_username("user1", "taken-name")

    @pytest.mark.asyncio
    async def test_item_not_found(self):
        from app.services.portfolio import ItemNotFoundError, PortfolioService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = PortfolioService(db)
        with pytest.raises(ItemNotFoundError):
            await svc.get_item("bad-id")

    @pytest.mark.asyncio
    async def test_delete_item_not_owner(self):
        from app.exceptions import AppError
        from app.services.portfolio import PortfolioService

        db = make_db()
        item = MagicMock()
        item.user_id = "other-user"
        db.get = AsyncMock(return_value=item)

        svc = PortfolioService(db)
        with pytest.raises(AppError, match="PERMISSION_DENIED"):
            await svc.delete_item("item1", "my-user")

    @pytest.mark.asyncio
    async def test_update_item_not_owner(self):
        from app.exceptions import AppError
        from app.services.portfolio import PortfolioService

        db = make_db()
        item = MagicMock()
        item.user_id = "other-user"
        db.get = AsyncMock(return_value=item)

        svc = PortfolioService(db)
        with pytest.raises(AppError, match="PERMISSION_DENIED"):
            await svc.update_item("item1", "my-user", title="New Title")

    @pytest.mark.asyncio
    async def test_toggle_badge_not_found(self):
        from app.exceptions import AppError
        from app.services.portfolio import PortfolioService

        db = make_db()
        db.get = AsyncMock(return_value=None)

        svc = PortfolioService(db)
        with pytest.raises(AppError, match="BADGE_NOT_FOUND"):
            await svc.toggle_badge("bad-id", "user1", True)

    @pytest.mark.asyncio
    async def test_toggle_badge_not_owner(self):
        from app.exceptions import AppError
        from app.services.portfolio import PortfolioService

        db = make_db()
        badge = MagicMock()
        badge.user_id = "other-user"
        db.get = AsyncMock(return_value=badge)

        svc = PortfolioService(db)
        with pytest.raises(AppError, match="PERMISSION_DENIED"):
            await svc.toggle_badge("badge1", "my-user", True)

    def test_portfolio_slug_generation(self):
        from app.services.portfolio import PortfolioService

        assert PortfolioService._generate_slug("AI Chatbot v2") == "ai-chatbot-v2"
        assert len(PortfolioService._generate_slug("AB")) >= 3

    @pytest.mark.asyncio
    async def test_get_public_profile_not_found(self):
        from app.services.portfolio import PortfolioService

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(None))

        svc = PortfolioService(db)
        result = await svc.get_public_profile("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_public_items_not_found(self):
        from app.services.portfolio import PortfolioService

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(None))

        svc = PortfolioService(db)
        result = await svc.get_public_items("nonexistent")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_public_item_not_found(self):
        from app.services.portfolio import PortfolioService

        db = make_db()
        db.execute = AsyncMock(return_value=mock_execute_returns(None))

        svc = PortfolioService(db)
        result = await svc.get_public_item("nonexistent", "slug")
        assert result is None
