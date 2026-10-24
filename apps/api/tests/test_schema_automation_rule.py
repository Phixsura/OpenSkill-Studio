"""Automation rule schema tests."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import CreateAutomationRuleRequest

VALID_ACTIONS = ["webhook", "sandbox_function", "api_call", "notification"]

@pytest.mark.parametrize("action", VALID_ACTIONS)
def test_valid_action_types(action):
    r = CreateAutomationRuleRequest(
        name="Rule",
        trigger_event="submission.completed",
        action_type=action,
        action_config={"url": "https://example.com"},
    )
    assert r.action_type == action

def test_missing_name():
    with pytest.raises(ValidationError):
        CreateAutomationRuleRequest(
            trigger_event="submission.completed",
            action_type="webhook",
            action_config={},
        )

def test_missing_trigger():
    with pytest.raises(ValidationError):
        CreateAutomationRuleRequest(
            name="Rule",
            action_type="webhook",
            action_config={},
        )

def test_missing_action_type():
    with pytest.raises(ValidationError):
        CreateAutomationRuleRequest(
            name="Rule",
            trigger_event="submission.completed",
            action_config={},
        )

def test_with_filter():
    r = CreateAutomationRuleRequest(
        name="Filtered",
        trigger_event="submission.completed",
        action_type="webhook",
        action_config={"url": "https://example.com"},
        trigger_filter={"field": "status", "operator": "eq", "value": "graded"},
    )
    assert r.trigger_filter is not None
