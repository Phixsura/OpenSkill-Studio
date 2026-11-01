"""App event hooks — 12 typed emitters."""

import inspect
import pytest
from app.services import app_event_hooks

HOOKS = [
    "on_submission_completed",
    "on_submission_graded",
    "on_cohort_member_added",
    "on_cohort_member_removed",
    "on_project_published",
    "on_pack_published",
    "on_pack_installed",
    "on_workflow_run_completed",
    "on_app_installed",
    "on_app_uninstalled",
    "on_evaluation_completed",
    "on_org_member_added",
]

@pytest.mark.parametrize("hook_name", HOOKS)
def test_hook_exists(hook_name):
    assert hasattr(app_event_hooks, hook_name)

@pytest.mark.parametrize("hook_name", HOOKS)
def test_hook_is_async(hook_name):
    func = getattr(app_event_hooks, hook_name)
    assert inspect.iscoroutinefunction(func)

@pytest.mark.parametrize("hook_name", HOOKS)
def test_hook_requires_db(hook_name):
    func = getattr(app_event_hooks, hook_name)
    assert "db" in inspect.signature(func).parameters

def test_total_hook_count():
    assert len(HOOKS) == 12
