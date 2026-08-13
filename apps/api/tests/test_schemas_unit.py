"""Schema validation branch coverage tests."""

import pytest
from pydantic import ValidationError

# ── Auth schemas ─────────────────────────────────────────


def test_password_too_long():
    from app.schemas.auth import RegisterRequest

    with pytest.raises(ValidationError):
        RegisterRequest(email="a@b.com", password="A1" + "x" * 127, display_name="Test")


def test_password_common():
    from app.schemas.auth import RegisterRequest

    with pytest.raises(ValidationError):
        RegisterRequest(email="a@b.com", password="Password1", display_name="Test")


def test_display_name_too_long():
    from app.schemas.auth import RegisterRequest

    with pytest.raises(ValidationError):
        RegisterRequest(email="a@b.com", password="Valid123!", display_name="X" * 101)


def test_change_password_common():
    from app.schemas.auth import ChangePasswordRequest

    with pytest.raises(ValidationError):
        ChangePasswordRequest(old_password="old", new_password="Password1")


def test_forgot_password_valid():
    from app.schemas.auth import ForgotPasswordRequest

    req = ForgotPasswordRequest(email="test@example.com")
    assert req.email == "test@example.com"


def test_reset_password_weak():
    from app.schemas.auth import ResetPasswordRequest

    with pytest.raises(ValidationError):
        ResetPasswordRequest(token="abc", new_password="short")


# ── Organization schemas ─────────────────────────────────


def test_org_name_too_short():
    from app.schemas.organization import CreateOrgRequest

    with pytest.raises(ValidationError):
        CreateOrgRequest(name="A")


def test_org_name_too_long():
    from app.schemas.organization import CreateOrgRequest

    with pytest.raises(ValidationError):
        CreateOrgRequest(name="X" * 101)


def test_invite_emails_empty():
    from app.schemas.organization import InviteMembersRequest

    with pytest.raises(ValidationError):
        InviteMembersRequest(emails=[])


def test_invite_emails_too_many():
    from app.schemas.organization import InviteMembersRequest

    with pytest.raises(ValidationError):
        InviteMembersRequest(emails=[f"u{i}@test.com" for i in range(101)])


# ── Portfolio schemas ────────────────────────────────────


def test_username_reserved():
    from app.schemas.portfolio import UsernameRequest

    with pytest.raises(ValidationError):
        UsernameRequest(username="admin")


def test_username_too_short():
    from app.schemas.portfolio import UsernameRequest

    with pytest.raises(ValidationError):
        UsernameRequest(username="ab")


def test_username_with_spaces():
    from app.schemas.portfolio import UsernameRequest

    with pytest.raises(ValidationError):
        UsernameRequest(username="has spaces")


def test_username_valid():
    from app.schemas.portfolio import UsernameRequest

    req = UsernameRequest(username="alice-wang")
    assert req.username == "alice-wang"


def test_website_url_invalid_scheme():
    from app.schemas.portfolio import UpdateProfileRequest

    with pytest.raises(ValidationError):
        UpdateProfileRequest(website_url="javascript:alert(1)")


def test_website_url_valid():
    from app.schemas.portfolio import UpdateProfileRequest

    req = UpdateProfileRequest(website_url="https://example.com")
    assert req.website_url == "https://example.com"


def test_social_links_invalid():
    from app.schemas.portfolio import UpdateProfileRequest

    with pytest.raises(ValidationError):
        UpdateProfileRequest(social_links={"github": "javascript:alert(1)"})


def test_social_links_valid():
    from app.schemas.portfolio import UpdateProfileRequest

    req = UpdateProfileRequest(social_links={"github": "https://github.com/alice"})
    assert req.social_links["github"] == "https://github.com/alice"


def test_portfolio_item_title_too_short():
    from app.schemas.portfolio import CreatePortfolioItemRequest

    with pytest.raises(ValidationError):
        CreatePortfolioItemRequest(title="A")


def test_portfolio_item_title_too_long():
    from app.schemas.portfolio import CreatePortfolioItemRequest

    with pytest.raises(ValidationError):
        CreatePortfolioItemRequest(title="X" * 201)


# ── Project schemas ──────────────────────────────────────


def test_project_title_too_long():
    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError):
        CreateProjectRequest(
            title="X" * 201,
            description="d",
            instructions="i",
            rubric=[{"criterion": "x", "max_score": 10}],
        )


def test_project_rubric_empty():
    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError):
        CreateProjectRequest(
            title="Valid",
            description="d",
            instructions="i",
            rubric=[],
        )


def test_deliverable_name_too_short():
    from app.schemas.project import CreateDeliverableRequest

    with pytest.raises(ValidationError):
        CreateDeliverableRequest(name="A", type="file")


def test_review_status_invalid():
    from app.schemas.project import CreateReviewRequest

    with pytest.raises(ValidationError):
        CreateReviewRequest(status="invalid_status")


def test_review_status_valid():
    from app.schemas.project import CreateReviewRequest

    req = CreateReviewRequest(status="approved")
    assert req.status == "approved"


# ── Skill schemas ────────────────────────────────────────


def test_category_name_too_short():
    from app.schemas.skill import CreateCategoryRequest

    with pytest.raises(ValidationError):
        CreateCategoryRequest(name="A")


def test_skill_name_too_long():
    from app.schemas.skill import CreateSkillRequest

    with pytest.raises(ValidationError):
        CreateSkillRequest(
            category_id="x",
            name="X" * 201,
            description="d",
        )


def test_exercise_title_too_short():
    from app.schemas.skill import CreateExerciseRequest

    with pytest.raises(ValidationError):
        CreateExerciseRequest(title="A", description="d", type="multiple_choice", config={})


def test_exercise_title_too_long():
    from app.schemas.skill import CreateExerciseRequest

    with pytest.raises(ValidationError):
        CreateExerciseRequest(title="X" * 201, description="d", type="multiple_choice", config={})


# ── Evaluation schemas ───────────────────────────────────


def test_trigger_type_invalid():
    from app.schemas.evaluation import TriggerEvaluationRequest

    with pytest.raises(ValidationError):
        TriggerEvaluationRequest(submission_id="x", type="invalid")


def test_trigger_type_valid():
    from app.schemas.evaluation import TriggerEvaluationRequest

    req = TriggerEvaluationRequest(submission_id="x", type="submission_review")
    assert req.type == "submission_review"
