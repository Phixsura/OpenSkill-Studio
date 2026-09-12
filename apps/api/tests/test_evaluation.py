"""AI evaluation pipeline tests."""

import json

import pytest

from app.core.llm import LLMResponse, calculate_cost
from app.models.evaluation import EvalStatus, EvalType
from app.services.evaluation import EvaluationService

# ── Auth protection ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_trigger_evaluation_requires_auth(client):
    r = await client.post(
        "/api/v1/orgs/fake/evaluation/trigger",
        json={
            "submission_id": "x",
            "type": "submission_review",
        },
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_list_eval_tasks_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/evaluation/tasks")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_eval_task_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/evaluation/tasks/fake-id")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_retry_eval_task_requires_auth(client):
    r = await client.post("/api/v1/orgs/fake/evaluation/tasks/fake-id/retry")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_cancel_eval_task_requires_auth(client):
    r = await client.post("/api/v1/orgs/fake/evaluation/tasks/fake-id/cancel")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_eval_usage_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/evaluation/usage")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_eval_settings_requires_auth(client):
    r = await client.get("/api/v1/orgs/fake/settings/evaluation")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_update_eval_settings_requires_auth(client):
    r = await client.put("/api/v1/orgs/fake/settings/evaluation", json={"enabled": True})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_eval_settings_null_clears_budget(client):
    """An explicit {"monthly_budget_usd": null} must CLEAR the budget
    (→ unlimited), while an empty/absent-field update leaves it unchanged.
    Regression for exclude_none dropping explicit nulls."""
    import uuid as _uuid

    from app.core.database import engine

    # Fresh pool: earlier tests may leave pooled connections bound to their
    # own (closed) event loops (same hygiene as test_auth.py)
    await engine.dispose()

    email = f"evalset-{_uuid.uuid4().hex[:8]}@test.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "display_name": "EvalSet"},
    )
    assert r.status_code == 201
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await client.post("/api/v1/orgs", json={"name": f"E-{_uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201
    oid = r.json()["data"]["id"]
    url = f"/api/v1/orgs/{oid}/settings/evaluation"

    # Set a budget
    r = await client.put(url, json={"monthly_budget_usd": 50}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["monthly_budget_usd"] == 50

    # Absent field → unchanged
    r = await client.put(url, json={}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["monthly_budget_usd"] == 50

    # Explicit null → cleared (unlimited)
    r = await client.put(url, json={"monthly_budget_usd": None}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["monthly_budget_usd"] is None

    await engine.dispose()


# ── Schema validation ────────────────────────────────────────


@pytest.mark.asyncio
async def test_trigger_invalid_type(client):
    r = await client.post(
        "/api/v1/orgs/fake/evaluation/trigger",
        json={
            "submission_id": "x",
            "type": "invalid",
        },
    )
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_trigger_missing_submission_id(client):
    r = await client.post(
        "/api/v1/orgs/fake/evaluation/trigger",
        json={
            "type": "submission_review",
        },
    )
    assert r.status_code in (401, 422)


# ── Unit tests: cost calculation ─────────────────────────────


def test_calculate_cost_anthropic():
    resp = LLMResponse(
        content="test",
        input_tokens=1000,
        output_tokens=500,
        model="claude-sonnet-5",
        provider="anthropic",
    )
    cost = calculate_cost(resp)
    # input: 1000 * 3.00 / 1M = 0.003, output: 500 * 15.00 / 1M = 0.0075
    assert cost == pytest.approx(0.0105, abs=0.0001)


def test_calculate_cost_openai():
    resp = LLMResponse(
        content="test",
        input_tokens=2000,
        output_tokens=1000,
        model="gpt-4o",
        provider="openai",
    )
    cost = calculate_cost(resp)
    # input: 2000 * 2.50 / 1M = 0.005, output: 1000 * 10.00 / 1M = 0.01
    assert cost == pytest.approx(0.015, abs=0.001)


def test_calculate_cost_unknown_model():
    # R67[6]: unknown models are charged at the flagship fallback tier —
    # $0 would exempt an org-selectable model from every budget while real
    # provider spend accrued.
    resp = LLMResponse(
        content="test",
        input_tokens=100,
        output_tokens=50,
        model="unknown-model",
        provider="unknown",
    )
    cost = calculate_cost(resp)
    assert cost > 0
    assert cost == round(100 * 3.00 / 1e6 + 50 * 15.00 / 1e6, 6)


# ── Unit tests: response parsing ─────────────────────────────


def test_parse_evaluation_response_valid():
    rubric = [
        {"criterion": "Quality", "max_score": 50},
        {"criterion": "Creativity", "max_score": 50},
    ]
    llm_output = json.dumps(
        {
            "scores": [
                {"criterion": "Quality", "score": 40, "max_score": 50, "feedback": "Good"},
                {"criterion": "Creativity", "score": 35, "max_score": 50, "feedback": "Nice"},
            ],
            "overall_feedback": "Well done",
            "strengths": ["Clear"],
            "improvements": ["More detail"],
        }
    )

    result = EvaluationService._parse_evaluation_response(llm_output, rubric)
    assert result["total_score"] == 75
    assert result["max_score"] == 100
    assert len(result["scores"]) == 2
    assert result["overall_feedback"] == "Well done"


def test_parse_evaluation_response_with_code_block():
    rubric = [{"criterion": "Test", "max_score": 100}]
    llm_output = """Here is my evaluation:
```json
{
  "scores": [{"criterion": "Test", "score": 80, "max_score": 100, "feedback": "OK"}],
  "overall_feedback": "Good",
  "strengths": [],
  "improvements": []
}
```"""

    result = EvaluationService._parse_evaluation_response(llm_output, rubric)
    assert result["total_score"] == 80


def test_parse_evaluation_response_clamps_score():
    rubric = [{"criterion": "Quality", "max_score": 50}]
    llm_output = json.dumps(
        {
            "scores": [{"criterion": "Quality", "score": 999, "max_score": 50, "feedback": ""}],
            "overall_feedback": "",
            "strengths": [],
            "improvements": [],
        }
    )

    result = EvaluationService._parse_evaluation_response(llm_output, rubric)
    assert result["scores"][0]["score"] == 50  # clamped


def test_parse_evaluation_response_negative_score():
    rubric = [{"criterion": "Quality", "max_score": 50}]
    llm_output = json.dumps(
        {
            "scores": [{"criterion": "Quality", "score": -10, "max_score": 50, "feedback": ""}],
            "overall_feedback": "",
            "strengths": [],
            "improvements": [],
        }
    )

    result = EvaluationService._parse_evaluation_response(llm_output, rubric)
    assert result["scores"][0]["score"] == 0  # clamped to 0


def test_parse_evaluation_invalid_json():
    rubric = [{"criterion": "Test", "max_score": 100}]
    with pytest.raises(json.JSONDecodeError):
        EvaluationService._parse_evaluation_response("not json", rubric)


# ── Unit tests: enums ────────────────────────────────────────


def test_eval_type_values():
    assert EvalType.EXERCISE_TEXT.value == "exercise_text"
    assert EvalType.EXERCISE_CODE.value == "exercise_code"
    assert EvalType.SUBMISSION_REVIEW.value == "submission_review"


def test_eval_status_values():
    assert EvalStatus.PENDING.value == "pending"
    assert EvalStatus.PROCESSING.value == "processing"
    assert EvalStatus.COMPLETED.value == "completed"
    assert EvalStatus.FAILED.value == "failed"
    assert EvalStatus.CANCELLED.value == "cancelled"


# ── Unit tests: rubric formatting ────────────────────────────


def test_format_rubric():
    rubric = [
        {"criterion": "Quality", "max_score": 50, "description": "Code quality"},
        {"criterion": "Design", "max_score": 30},
    ]
    result = EvaluationService._format_rubric(rubric)
    assert "Quality" in result
    assert "0-50 points" in result
    assert "Code quality" in result
    assert "Design" in result


def test_format_submission_with_content():
    from unittest.mock import MagicMock

    item1 = MagicMock()
    item1.content = "My answer text"
    item1.file_name = None

    item2 = MagicMock()
    item2.content = None
    item2.file_name = "code.py"

    result = EvaluationService._format_submission([item1, item2])
    assert "My answer text" in result
    assert "[File: code.py]" in result


def test_format_submission_empty():
    result = EvaluationService._format_submission([])
    assert "No content" in result


@pytest.mark.asyncio
async def test_multimodal_eval_types_persist_not_500(client):
    """R86: SQLAlchemy persists the enum MEMBER NAME (IMAGE_REVIEW), but
    migration 65cf240e added the four multimodal labels to the Postgres
    eval_type enum as lowercase VALUES (image_review). Triggering any of them
    hit InvalidTextRepresentationError → unhandled 500. Migration
    a1b2c3d4e5f6 renames the labels to uppercase names. With AI eval enabled,
    each multimodal type must create the task (201), never 500."""
    import uuid as _uuid

    from app.core.database import engine

    await engine.dispose()

    email = f"mm-{_uuid.uuid4().hex[:8]}@test.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "display_name": "MM"},
    )
    assert r.status_code == 201
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    oid = (
        await client.post("/api/v1/orgs", json={"name": f"MM-{_uuid.uuid4().hex[:8]}"}, headers=h)
    ).json()["data"]["id"]

    # Enable AI eval so the trigger reaches the DB write (past EVAL_NOT_ENABLED)
    r = await client.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={"enabled": True, "monthly_budget_usd": 100},
        headers=h,
    )
    assert r.status_code == 200, r.text

    proj = (
        await client.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "MM Proj",
                "description": "d" * 20,
                "instructions": "do it",
                "project_type": "general",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await client.post(f"/api/v1/orgs/{oid}/projects/{proj}/publish", headers=h)
    sub = (
        await client.post(
            f"/api/v1/orgs/{oid}/projects/{proj}/submissions", json={"content": "w"}, headers=h
        )
    ).json()["data"]["id"]
    await client.post(f"/api/v1/orgs/{oid}/projects/{proj}/submissions/{sub}/submit", headers=h)

    for t in ("image_review", "video_review", "prompt_review", "commercial_submission_review"):
        r = await client.post(
            f"/api/v1/orgs/{oid}/evaluation/trigger",
            json={"submission_id": sub, "type": t},
            headers=h,
        )
        # The enum write must succeed (task created). Never a 500 (the bug).
        assert r.status_code != 500, f"{t}: 500 — eval_type enum label mismatch: {r.text[:200]}"
        assert r.status_code == 201, f"{t}: {r.status_code} {r.text[:200]}"
        assert r.json()["data"]["type"] == t

    await engine.dispose()
