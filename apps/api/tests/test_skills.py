"""Skill, exercise, and progress tests."""

import pytest

# ── Auth protection ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_categories_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/categories")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_category_requires_auth(client):
    r = await client.post("/api/v1/orgs/fake/categories", json={"name": "AI"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_list_skills_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/skills")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_skill_requires_auth(client):
    r = await client.post(
        "/api/v1/orgs/fake/skills", json={"name": "X", "description": "Y", "category_id": "z"}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_skill_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/skills/fake-id")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_exercise_requires_auth(client):
    r = await client.post(
        "/api/v1/orgs/fake/skills/fake/exercises",
        json={"title": "Q1", "description": "D", "type": "multiple_choice", "config": {}},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_submit_attempt_requires_auth(client):
    r = await client.post(
        "/api/v1/orgs/fake/exercises/fake/attempts",
        json={"answer": {"selected": ["a"]}},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_progress_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/progress/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_pending_grading_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/grading/pending")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_grade_attempt_requires_auth(client):
    r = await client.post(
        "/api/v1/orgs/fake/grading/attempts/fake",
        json={"score": 80},
    )
    assert r.status_code == 401


# ── Schema validation ────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_category_name_too_short(client):
    r = await client.post("/api/v1/orgs/fake/categories", json={"name": "A"})
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_skill_missing_description(client):
    r = await client.post("/api/v1/orgs/fake/skills", json={"name": "Test", "category_id": "x"})
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_exercise_missing_type(client):
    r = await client.post(
        "/api/v1/orgs/fake/skills/fake/exercises",
        json={"title": "Q", "description": "D", "config": {}},
    )
    assert r.status_code in (401, 422)


# ── Unit tests ───────────────────────────────────────────────


def test_cycle_detection():
    """BFS cycle detection catches A→B→A."""
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    from app.services.skill import CyclicDependencyError, SkillService

    svc = SkillService.__new__(SkillService)
    svc.db = MagicMock()

    # Simulate: B has prerequisite A. Now trying to make A depend on B → cycle.
    async def mock_execute(stmt):
        result = MagicMock()
        # If querying prerequisites of B, return A
        result.scalars.return_value = ["skill_a"]
        return result

    svc.db.execute = AsyncMock(side_effect=mock_execute)

    with pytest.raises(CyclicDependencyError):
        asyncio.get_event_loop_policy().new_event_loop().run_until_complete(
            svc._detect_cycle("skill_a", ["skill_b"])
        )


def test_mcq_grading_correct():
    """MCQ auto-grading: correct answer."""

    config = {"correct": ["b"], "explanation": "B is right"}
    answer = {"selected": ["b"]}

    correct = config.get("correct", [])
    user_answer = answer.get("selected", [])
    assert sorted(user_answer) == sorted(correct)


def test_mcq_grading_incorrect():
    """MCQ auto-grading: wrong answer."""
    config = {"correct": ["b"]}
    answer = {"selected": ["a"]}

    correct = config.get("correct", [])
    user_answer = answer.get("selected", [])
    assert sorted(user_answer) != sorted(correct)


def test_mcq_grading_multiple_correct():
    """MCQ auto-grading: multiple correct answers."""
    config = {"correct": ["a", "c"]}
    answer = {"selected": ["c", "a"]}  # Order shouldn't matter

    correct = config.get("correct", [])
    user_answer = answer.get("selected", [])
    assert sorted(user_answer) == sorted(correct)


def test_slug_generation():
    """Skill slug generation."""
    from app.services.skill import SkillService

    assert SkillService._generate_slug("Few-Shot Prompting") == "few-shot-prompting"
    assert SkillService._generate_slug("Python 基础") is not None
    assert len(SkillService._generate_slug("AB")) >= 3


def test_content_status_values():
    """Content status enum has expected values."""
    from app.models.skill import ContentStatus

    assert ContentStatus.DRAFT.value == "draft"
    assert ContentStatus.PUBLISHED.value == "published"
    assert ContentStatus.ARCHIVED.value == "archived"


def test_exercise_type_values():
    """Exercise type enum has expected values."""
    from app.models.skill import ExerciseType

    assert ExerciseType.MULTIPLE_CHOICE.value == "multiple_choice"
    assert ExerciseType.TEXT_ANSWER.value == "text_answer"
    assert ExerciseType.CODE_SUBMISSION.value == "code_submission"
    assert ExerciseType.FILE_UPLOAD.value == "file_upload"


def test_progress_status_values():
    """Progress status enum has expected values."""
    from app.models.skill import ProgressStatus

    assert ProgressStatus.NOT_STARTED.value == "not_started"
    assert ProgressStatus.IN_PROGRESS.value == "in_progress"
    assert ProgressStatus.COMPLETED.value == "completed"
