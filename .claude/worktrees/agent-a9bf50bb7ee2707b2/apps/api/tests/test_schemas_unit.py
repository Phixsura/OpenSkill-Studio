"""Comprehensive schema validator tests for full branch coverage."""

import pytest
from pydantic import ValidationError


class TestAuthSchemas:
    def test_register_password_too_long(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(ValidationError, match="128"):
            RegisterRequest(email="a@b.com", password="A1" + "x" * 127, display_name="Test")

    def test_register_common_password(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(ValidationError, match="common"):
            RegisterRequest(email="a@b.com", password="Password123", display_name="Test")

    def test_register_valid(self):
        from app.schemas.auth import RegisterRequest
        r = RegisterRequest(email="a@b.com", password="Valid1234!", display_name="Test User")
        assert r.email == "a@b.com"

    def test_register_display_name_stripped(self):
        from app.schemas.auth import RegisterRequest
        r = RegisterRequest(email="a@b.com", password="Valid1234!", display_name="  Alice  ")
        assert r.display_name == "Alice"

    def test_register_display_name_too_long(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(ValidationError, match="100"):
            RegisterRequest(email="a@b.com", password="Valid1234!", display_name="x" * 101)

    def test_change_password_common_rejected(self):
        from app.schemas.auth import ChangePasswordRequest
        with pytest.raises(ValidationError, match="common"):
            ChangePasswordRequest(old_password="old", new_password="Password123")

    def test_forgot_password_valid(self):
        from app.schemas.auth import ForgotPasswordRequest
        r = ForgotPasswordRequest(email="test@example.com")
        assert r.email == "test@example.com"

    def test_reset_password_weak(self):
        from app.schemas.auth import ResetPasswordRequest
        with pytest.raises(ValidationError):
            ResetPasswordRequest(token="abc", new_password="weak")

    def test_reset_password_valid(self):
        from app.schemas.auth import ResetPasswordRequest
        r = ResetPasswordRequest(token="abc", new_password="StrongPass1!")
        assert r.token == "abc"

    def test_session_response(self):
        from datetime import datetime, timezone
        from app.schemas.auth import SessionResponse
        s = SessionResponse(id="01", device_info="Chrome", ip_address="1.2.3.4",
            created_at=datetime.now(timezone.utc), expires_at=datetime.now(timezone.utc))
        assert s.id == "01"


class TestOrgSchemas:
    def test_create_org_name_too_short(self):
        from app.schemas.organization import CreateOrgRequest
        with pytest.raises(ValidationError, match="2"):
            CreateOrgRequest(name="A")

    def test_create_org_name_too_long(self):
        from app.schemas.organization import CreateOrgRequest
        with pytest.raises(ValidationError, match="100"):
            CreateOrgRequest(name="x" * 101)

    def test_create_org_valid(self):
        from app.schemas.organization import CreateOrgRequest
        r = CreateOrgRequest(name="Test Org", slug="test-org")
        assert r.name == "Test Org"

    def test_invite_members_empty_emails(self):
        from app.schemas.organization import InviteMembersRequest
        with pytest.raises(ValidationError, match="one email"):
            InviteMembersRequest(emails=[], role="student")

    def test_invite_members_too_many(self):
        from app.schemas.organization import InviteMembersRequest
        with pytest.raises(ValidationError, match="100"):
            InviteMembersRequest(emails=[f"u{i}@x.com" for i in range(101)], role="student")

    def test_invite_members_valid(self):
        from app.schemas.organization import InviteMembersRequest
        r = InviteMembersRequest(emails=["a@b.com"], role="student")
        assert len(r.emails) == 1


class TestPortfolioSchemas:
    def test_username_reserved(self):
        from app.schemas.portfolio import UsernameRequest
        with pytest.raises(ValidationError, match="reserved"):
            UsernameRequest(username="admin")

    def test_username_too_short(self):
        from app.schemas.portfolio import UsernameRequest
        with pytest.raises(ValidationError, match="4-40"):
            UsernameRequest(username="ab")

    def test_username_uppercase(self):
        from app.schemas.portfolio import UsernameRequest
        with pytest.raises(ValidationError):
            UsernameRequest(username="Alice")

    def test_username_valid(self):
        from app.schemas.portfolio import UsernameRequest
        r = UsernameRequest(username="alice-wang")
        assert r.username == "alice-wang"

    def test_website_url_invalid_scheme(self):
        from app.schemas.portfolio import UpdateProfileRequest
        with pytest.raises(ValidationError, match="http"):
            UpdateProfileRequest(website_url="ftp://example.com")

    def test_website_url_valid(self):
        from app.schemas.portfolio import UpdateProfileRequest
        r = UpdateProfileRequest(website_url="https://example.com")
        assert r.website_url == "https://example.com"

    def test_social_links_invalid_scheme(self):
        from app.schemas.portfolio import UpdateProfileRequest
        with pytest.raises(ValidationError, match="http"):
            UpdateProfileRequest(social_links={"github": "javascript:alert(1)"})

    def test_social_links_valid(self):
        from app.schemas.portfolio import UpdateProfileRequest
        r = UpdateProfileRequest(social_links={"github": "https://github.com/alice"})
        assert r.social_links is not None

    def test_create_item_title_too_short(self):
        from app.schemas.portfolio import CreatePortfolioItemRequest
        with pytest.raises(ValidationError, match="2-200"):
            CreatePortfolioItemRequest(title="A")

    def test_create_item_valid(self):
        from app.schemas.portfolio import CreatePortfolioItemRequest
        r = CreatePortfolioItemRequest(title="My Project")
        assert r.title == "My Project"


class TestProjectSchemas:
    def test_create_project_title_too_short(self):
        from app.schemas.project import CreateProjectRequest
        with pytest.raises(ValidationError, match="2-200"):
            CreateProjectRequest(title="A", description="D", instructions="I",
                rubric=[{"criterion": "X", "max_score": 10}])

    def test_create_project_empty_rubric(self):
        from app.schemas.project import CreateProjectRequest
        with pytest.raises(ValidationError, match="one criterion"):
            CreateProjectRequest(title="Test", description="D", instructions="I", rubric=[])

    def test_create_project_valid(self):
        from app.schemas.project import CreateProjectRequest
        r = CreateProjectRequest(title="Test Project", description="D", instructions="I",
            rubric=[{"criterion": "X", "max_score": 10}])
        assert r.max_score == 100

    def test_create_deliverable_name_too_short(self):
        from app.schemas.project import CreateDeliverableRequest
        with pytest.raises(ValidationError, match="2-200"):
            CreateDeliverableRequest(name="A", type="file")

    def test_create_review_invalid_status(self):
        from app.schemas.project import CreateReviewRequest
        with pytest.raises(ValidationError, match="Status"):
            CreateReviewRequest(status="invalid")

    def test_create_review_valid(self):
        from app.schemas.project import CreateReviewRequest
        r = CreateReviewRequest(status="approved", score=90)
        assert r.score == 90


class TestSkillSchemas:
    def test_create_category_name_short(self):
        from app.schemas.skill import CreateCategoryRequest
        with pytest.raises(ValidationError, match="2-100"):
            CreateCategoryRequest(name="A")

    def test_create_category_name_long(self):
        from app.schemas.skill import CreateCategoryRequest
        with pytest.raises(ValidationError, match="2-100"):
            CreateCategoryRequest(name="x" * 101)

    def test_create_category_valid(self):
        from app.schemas.skill import CreateCategoryRequest
        r = CreateCategoryRequest(name="AI Skills")
        assert r.name == "AI Skills"

    def test_create_skill_name_short(self):
        from app.schemas.skill import CreateSkillRequest
        with pytest.raises(ValidationError, match="2-200"):
            CreateSkillRequest(name="A", description="D", category_id="c")

    def test_create_exercise_title_short(self):
        from app.schemas.skill import CreateExerciseRequest
        with pytest.raises(ValidationError, match="2-200"):
            CreateExerciseRequest(title="A", description="D", type="multiple_choice", config={})

    def test_create_exercise_valid(self):
        from app.schemas.skill import CreateExerciseRequest
        r = CreateExerciseRequest(title="Quiz 1", description="D", type="multiple_choice", config={})
        assert r.max_score == 100


class TestEvalSchemas:
    def test_trigger_invalid_type(self):
        from app.schemas.evaluation import TriggerEvaluationRequest
        with pytest.raises(ValidationError, match="Type"):
            TriggerEvaluationRequest(submission_id="x", type="invalid")

    def test_trigger_valid(self):
        from app.schemas.evaluation import TriggerEvaluationRequest
        r = TriggerEvaluationRequest(submission_id="x")
        assert r.type == "submission_review"

    def test_eval_settings_response(self):
        from app.schemas.evaluation import EvalSettingsResponse
        r = EvalSettingsResponse(enabled=True, monthly_budget_usd=50.0,
            default_model="claude-sonnet-5", auto_evaluate=True, pass_threshold=0.6)
        assert r.enabled
