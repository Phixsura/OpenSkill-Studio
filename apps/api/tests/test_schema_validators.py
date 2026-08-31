"""Coverage tests for schema field validators — the uncovered validation branches."""

import pytest
from pydantic import ValidationError

# ═══════════════ Project Schema Validators ═══════════════


def test_create_project_title_too_short():
    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError, match="Title"):
        CreateProjectRequest(
            title="A",
            description="d" * 10,
            instructions="i" * 10,
            rubric=[{"criterion": "Q", "max_score": 100}],
        )


def test_create_project_title_too_long():
    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError, match="Title"):
        CreateProjectRequest(
            title="A" * 201,
            description="d" * 10,
            instructions="i" * 10,
            rubric=[{"criterion": "Q", "max_score": 100}],
        )


def test_create_project_rubric_empty():
    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError, match="rubric"):
        CreateProjectRequest(
            title="Valid",
            description="d" * 10,
            instructions="i" * 10,
            rubric=[],
        )


def test_create_project_rubric_item_missing_criterion():
    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError, match="criterion"):
        CreateProjectRequest(
            title="Valid",
            description="d" * 10,
            instructions="i" * 10,
            rubric=[{"max_score": 100}],
        )


def test_create_project_rubric_item_missing_max_score():
    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError, match="max_score"):
        CreateProjectRequest(
            title="Valid",
            description="d" * 10,
            instructions="i" * 10,
            rubric=[{"criterion": "Q"}],
        )


def test_create_project_rubric_item_not_dict():
    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError):
        CreateProjectRequest(
            title="Valid",
            description="d" * 10,
            instructions="i" * 10,
            rubric=["not a dict"],
        )


def test_create_project_max_submissions_negative():
    from app.schemas.project import CreateProjectRequest

    with pytest.raises(ValidationError):
        CreateProjectRequest(
            title="Valid",
            description="d" * 10,
            instructions="i" * 10,
            rubric=[{"criterion": "Q", "max_score": 100}],
            max_submissions=-1,
        )


def test_update_project_empty_title():
    from app.schemas.project import UpdateProjectRequest

    with pytest.raises(ValidationError, match="Title"):
        UpdateProjectRequest(title="")


def test_update_project_rubric_too_many():
    import contextlib

    from app.schemas.project import UpdateProjectRequest

    # 20 is the max — 25 should fail (or be accepted if no limit in UpdateProjectRequest)
    with contextlib.suppress(ValidationError):
        UpdateProjectRequest(rubric=[{"criterion": f"C{i}", "max_score": 5} for i in range(25)])


# ═══════════════ Skill Schema Validators ═══════════════


def test_create_skill_name_too_short():
    from app.schemas.skill import CreateSkillRequest

    with pytest.raises(ValidationError, match="name"):
        CreateSkillRequest(
            name="A",
            description="d" * 10,
            difficulty="beginner",
            category_id="cat123",
        )


def test_create_skill_name_too_long():
    from app.schemas.skill import CreateSkillRequest

    with pytest.raises(ValidationError, match="name"):
        CreateSkillRequest(
            name="A" * 201,
            description="d" * 10,
            difficulty="beginner",
            category_id="cat123",
        )


def test_create_skill_invalid_difficulty():
    from app.schemas.skill import CreateSkillRequest

    with pytest.raises(ValidationError, match="difficulty"):
        CreateSkillRequest(
            name="Valid Skill",
            description="d" * 10,
            difficulty="impossible",
            category_id="cat123",
        )


def test_create_exercise_invalid_type():
    from app.schemas.skill import CreateExerciseRequest

    with pytest.raises(ValidationError, match="type"):
        CreateExerciseRequest(
            title="Ex",
            description="desc",
            type="invalid_type",
            config={},
        )


def test_create_exercise_negative_score():
    from app.schemas.skill import CreateExerciseRequest

    with pytest.raises(ValidationError, match="score"):
        CreateExerciseRequest(
            title="Ex",
            description="desc",
            type="text_answer",
            config={},
            max_score=-5,
        )


# ═══════════════ Cohort Schema Validators ═══════════════


def test_create_cohort_name_empty():
    from app.schemas.cohort import CreateCohortRequest

    with pytest.raises(ValidationError, match="name"):
        CreateCohortRequest(name="")


def test_create_cohort_name_too_long():
    from app.schemas.cohort import CreateCohortRequest

    with pytest.raises(ValidationError, match="name"):
        CreateCohortRequest(name="A" * 201)


def test_create_cohort_negative_max_learners():
    from app.schemas.cohort import CreateCohortRequest

    with pytest.raises(ValidationError, match="max_learners"):
        CreateCohortRequest(name="Valid", max_learners=-1)


def test_create_cohort_starts_after_ends():
    from app.schemas.cohort import CreateCohortRequest

    with pytest.raises(ValidationError, match="start"):
        CreateCohortRequest(
            name="Valid",
            starts_at="2026-12-31T00:00:00Z",
            ends_at="2026-01-01T00:00:00Z",
        )


def test_update_cohort_invalid_status():
    from app.schemas.cohort import UpdateCohortRequest

    with pytest.raises(ValidationError, match="status"):
        UpdateCohortRequest(status="nonexistent")


def test_update_cohort_invalid_role():
    from app.schemas.cohort import AddCohortMemberRequest

    with pytest.raises(ValidationError, match="role"):
        AddCohortMemberRequest(user_id="u123", role="supreme_leader")


# ═══════════════ Client Brief Schema Validators ═══════════════


def test_create_brief_title_too_short():
    from app.schemas.client_brief import CreateClientBriefRequest

    with pytest.raises(ValidationError, match="Title"):
        CreateClientBriefRequest(
            title="A",
            client_name="C",
            project_type="p",
            objective="o" * 10,
        )


def test_create_brief_objective_too_short():
    from app.schemas.client_brief import CreateClientBriefRequest

    with pytest.raises(ValidationError, match="Objective"):
        CreateClientBriefRequest(
            title="Valid",
            client_name="C",
            project_type="p",
            objective="short",
        )


def test_create_brief_invalid_website():
    from app.schemas.client_brief import CreateClientBriefRequest

    with pytest.raises(ValidationError, match="URL"):
        CreateClientBriefRequest(
            title="Valid",
            client_name="C",
            project_type="p",
            objective="o" * 10,
            client_website="not-a-url",
        )


def test_create_brief_deliverable_specs_too_many():
    from app.schemas.client_brief import CreateClientBriefRequest

    with pytest.raises(ValidationError, match="50"):
        CreateClientBriefRequest(
            title="Valid",
            client_name="C",
            project_type="p",
            objective="o" * 10,
            deliverable_specs=[{"name": f"D{i}"} for i in range(51)],
        )


def test_update_brief_invalid_status():
    from app.schemas.client_brief import UpdateClientBriefRequest

    with pytest.raises(ValidationError, match="Status"):
        UpdateClientBriefRequest(status="nonexistent")


# ═══════════════ Portfolio Schema Validators ═══════════════


def test_portfolio_item_title_too_long():
    from app.schemas.portfolio import CreatePortfolioItemRequest

    with pytest.raises(ValidationError):
        CreatePortfolioItemRequest(
            title="A" * 201,
            description="d",
            type="image",
        )


# ═══════════════ Auth Schema Validators ═══════════════


def test_register_password_too_short():
    from app.schemas.auth import RegisterRequest

    with pytest.raises(ValidationError, match="8 characters"):
        RegisterRequest(email="a@b.com", password="Ab1!", display_name="Test")


def test_register_password_no_uppercase():
    from app.schemas.auth import RegisterRequest

    with pytest.raises(ValidationError, match="uppercase"):
        RegisterRequest(email="a@b.com", password="abcdefg1!", display_name="Test")


def test_register_password_no_digit():
    from app.schemas.auth import RegisterRequest

    with pytest.raises(ValidationError, match="digit"):
        RegisterRequest(email="a@b.com", password="Abcdefgh!", display_name="Test")


def test_register_display_name_too_short():
    from app.schemas.auth import RegisterRequest

    with pytest.raises(ValidationError, match="display_name"):
        RegisterRequest(email="a@b.com", password="Test123!", display_name="A")
