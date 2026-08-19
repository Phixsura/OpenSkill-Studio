"""Coverage for schema validator error branches — Update schemas + edge cases."""

import pytest
from pydantic import ValidationError

# ═══════════════ Client Brief Update Validators ═══════════════


def test_update_brief_title_too_short():
    from app.schemas.client_brief import UpdateClientBriefRequest
    with pytest.raises(ValidationError, match="Title"):
        UpdateClientBriefRequest(title="A")


def test_update_brief_client_name_empty():
    from app.schemas.client_brief import UpdateClientBriefRequest
    with pytest.raises(ValidationError, match="Client name"):
        UpdateClientBriefRequest(client_name="")


def test_update_brief_objective_too_short():
    from app.schemas.client_brief import UpdateClientBriefRequest
    with pytest.raises(ValidationError, match="Objective"):
        UpdateClientBriefRequest(objective="short")


def test_update_brief_objective_too_long():
    from app.schemas.client_brief import UpdateClientBriefRequest
    with pytest.raises(ValidationError, match="10,000"):
        UpdateClientBriefRequest(objective="x" * 10001)


# ═══════════════ Client Brief Create — More Branches ═══════════════


def test_create_brief_project_type_too_long():
    from app.schemas.client_brief import CreateClientBriefRequest
    with pytest.raises(ValidationError, match="Project type"):
        CreateClientBriefRequest(
            title="Valid", client_name="C", project_type="p" * 51,
            objective="o" * 10,
        )


def test_create_brief_text_field_too_long():
    from app.schemas.client_brief import CreateClientBriefRequest
    with pytest.raises(ValidationError, match="10,000"):
        CreateClientBriefRequest(
            title="Valid", client_name="C", project_type="p",
            objective="o" * 10,
            target_audience="x" * 10001,
        )


def test_create_brief_website_too_long():
    from app.schemas.client_brief import CreateClientBriefRequest
    with pytest.raises(ValidationError, match="URL"):
        CreateClientBriefRequest(
            title="Valid", client_name="C", project_type="p",
            objective="o" * 10,
            client_website="https://" + "x" * 500,
        )


def test_create_brief_list_data_too_large():
    from app.schemas.client_brief import CreateClientBriefRequest
    with pytest.raises(ValidationError):
        CreateClientBriefRequest(
            title="Valid", client_name="C", project_type="p",
            objective="o" * 10,
            deliverable_specs=[{"data": "x" * 5000} for _ in range(20)],
        )


def test_create_brief_budget_range_too_long():
    from app.schemas.client_brief import CreateClientBriefRequest
    with pytest.raises(ValidationError, match="Budget"):
        CreateClientBriefRequest(
            title="Valid", client_name="C", project_type="p",
            objective="o" * 10,
            budget_range="$" * 101,
        )


def test_create_brief_timeline_too_long():
    from app.schemas.client_brief import CreateClientBriefRequest
    with pytest.raises(ValidationError, match="Timeline"):
        CreateClientBriefRequest(
            title="Valid", client_name="C", project_type="p",
            objective="o" * 10,
            timeline="w" * 201,
        )


# ═══════════════ Convert Brief Validators ═══════════════


def test_convert_brief_title_too_short():
    from app.schemas.client_brief import ConvertBriefToProjectRequest
    with pytest.raises(ValidationError, match="Title"):
        ConvertBriefToProjectRequest(
            title="A", rubric=[{"criterion": "Q", "max_score": 100}],
        )


def test_convert_brief_rubric_empty():
    from app.schemas.client_brief import ConvertBriefToProjectRequest
    with pytest.raises(ValidationError, match="rubric"):
        ConvertBriefToProjectRequest(rubric=[])


def test_convert_brief_rubric_too_many():
    from app.schemas.client_brief import ConvertBriefToProjectRequest
    with pytest.raises(ValidationError, match="20"):
        ConvertBriefToProjectRequest(
            rubric=[{"criterion": f"C{i}", "max_score": 5} for i in range(21)],
        )


def test_convert_brief_rubric_missing_fields():
    from app.schemas.client_brief import ConvertBriefToProjectRequest
    with pytest.raises(ValidationError, match="criterion"):
        ConvertBriefToProjectRequest(rubric=[{"max_score": 100}])


def test_convert_brief_max_submissions_negative():
    from app.schemas.client_brief import ConvertBriefToProjectRequest
    with pytest.raises(ValidationError, match="max_submissions"):
        ConvertBriefToProjectRequest(
            rubric=[{"criterion": "Q", "max_score": 100}],
            max_submissions=-1,
        )


# ═══════════════ Project Schema — More Branches ═══════════════


def test_create_project_description_too_long():
    from app.schemas.project import CreateProjectRequest
    with pytest.raises(ValidationError):
        CreateProjectRequest(
            title="Valid", description="d" * 10001, instructions="i" * 10,
            rubric=[{"criterion": "Q", "max_score": 100}],
        )


def test_create_project_rubric_too_many():
    from app.schemas.project import CreateProjectRequest
    with pytest.raises(ValidationError):
        CreateProjectRequest(
            title="Valid", description="d" * 10, instructions="i" * 10,
            rubric=[{"criterion": f"C{i}", "max_score": 5} for i in range(21)],
        )


def test_create_project_max_score_negative():
    from app.schemas.project import CreateProjectRequest
    with pytest.raises(ValidationError):
        CreateProjectRequest(
            title="Valid", description="d" * 10, instructions="i" * 10,
            rubric=[{"criterion": "Q", "max_score": 100}],
            max_score=-1,
        )


# ═══════════════ Skill Schema — More Branches ═══════════════


def test_create_skill_description_too_long():
    from app.schemas.skill import CreateSkillRequest
    with pytest.raises(ValidationError):
        CreateSkillRequest(
            name="Valid Skill", description="d" * 10001,
            difficulty="beginner", category_id="cat123",
        )


def test_update_skill_name_empty():
    from app.schemas.skill import UpdateSkillRequest
    with pytest.raises(ValidationError):
        UpdateSkillRequest(name="")


def test_create_category_name_empty():
    from app.schemas.skill import CreateCategoryRequest
    with pytest.raises(ValidationError):
        CreateCategoryRequest(name="")


def test_create_category_name_too_long():
    from app.schemas.skill import CreateCategoryRequest
    with pytest.raises(ValidationError):
        CreateCategoryRequest(name="A" * 101)


# ═══════════════ Cohort Schema — More Branches ═══════════════


def test_create_cohort_max_learners_zero():
    from app.schemas.cohort import CreateCohortRequest
    with pytest.raises(ValidationError, match="max_learners"):
        CreateCohortRequest(name="Valid", max_learners=0)


def test_cohort_response_validates():
    from app.schemas.cohort import CohortResponse
    data = {
        "id": "abc", "org_id": "org1", "name": "Test",
        "slug": "test", "description": None, "status": "draft",
        "starts_at": None, "ends_at": None, "max_learners": None,
        "settings": {}, "created_by": "u1", "member_count": 0,
        "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
    }
    resp = CohortResponse(**data)
    assert resp.name == "Test"


# ═══════════════ Portfolio Schema — Branches ═══════════════


def test_portfolio_update_visibility_invalid():
    from app.schemas.portfolio import UpdatePortfolioItemRequest
    with pytest.raises(ValidationError):
        UpdatePortfolioItemRequest(visibility="invalid")


def test_portfolio_profile_update():
    from app.schemas.portfolio import UpdateProfileRequest
    req = UpdateProfileRequest(headline="New headline")
    assert req.headline == "New headline"
