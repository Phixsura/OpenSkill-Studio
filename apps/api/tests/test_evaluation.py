"""AI evaluation pipeline tests."""

import json

import pytest

from app.core.llm import LLMResponse, calculate_cost
from app.models.evaluation import EvalStatus, EvalType
from app.services.evaluation import EvaluationService

# ── Auth protection ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_trigger_evaluation_requires_auth(client):
    r = await client.post("/api/v1/orgs/fake/evaluation/trigger", json={
        "submission_id": "x", "type": "submission_review",
    })
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


# ── Schema validation ────────────────────────────────────────


@pytest.mark.asyncio
async def test_trigger_invalid_type(client):
    r = await client.post("/api/v1/orgs/fake/evaluation/trigger", json={
        "submission_id": "x", "type": "invalid",
    })
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_trigger_missing_submission_id(client):
    r = await client.post("/api/v1/orgs/fake/evaluation/trigger", json={
        "type": "submission_review",
    })
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
    resp = LLMResponse(
        content="test", input_tokens=100, output_tokens=50,
        model="unknown-model", provider="unknown",
    )
    cost = calculate_cost(resp)
    assert cost == 0


# ── Unit tests: response parsing ─────────────────────────────


def test_parse_evaluation_response_valid():
    rubric = [
        {"criterion": "Quality", "max_score": 50},
        {"criterion": "Creativity", "max_score": 50},
    ]
    llm_output = json.dumps({
        "scores": [
            {"criterion": "Quality", "score": 40, "max_score": 50, "feedback": "Good"},
            {"criterion": "Creativity", "score": 35, "max_score": 50, "feedback": "Nice"},
        ],
        "overall_feedback": "Well done",
        "strengths": ["Clear"],
        "improvements": ["More detail"],
    })

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
    llm_output = json.dumps({
        "scores": [{"criterion": "Quality", "score": 999, "max_score": 50, "feedback": ""}],
        "overall_feedback": "",
        "strengths": [],
        "improvements": [],
    })

    result = EvaluationService._parse_evaluation_response(llm_output, rubric)
    assert result["scores"][0]["score"] == 50  # clamped


def test_parse_evaluation_response_negative_score():
    rubric = [{"criterion": "Quality", "max_score": 50}]
    llm_output = json.dumps({
        "scores": [{"criterion": "Quality", "score": -10, "max_score": 50, "feedback": ""}],
        "overall_feedback": "",
        "strengths": [],
        "improvements": [],
    })

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
