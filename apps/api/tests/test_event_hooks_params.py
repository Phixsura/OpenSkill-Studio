"""Event hooks — verify each hook has the right domain-specific params."""

import inspect
import pytest
from app.services import app_event_hooks as hooks

HOOK_PARAMS = [
    ("on_submission_completed", ["submission_id"]),
    ("on_submission_graded", ["submission_id"]),
    ("on_cohort_member_added", ["cohort_id", "user_id"]),
    ("on_cohort_member_removed", ["cohort_id", "user_id"]),
    ("on_project_published", ["project_id"]),
    ("on_pack_published", ["pack_id"]),
    ("on_pack_installed", ["pack_id"]),
    ("on_workflow_run_completed", ["run_id"]),
    ("on_app_installed", ["app_id"]),
    ("on_app_uninstalled", ["app_id"]),
    ("on_evaluation_completed", ["evaluation_id"]),
    ("on_org_member_added", ["org_id", "user_id"]),
]

@pytest.mark.parametrize("hook,expected_params", HOOK_PARAMS, ids=lambda x: x if isinstance(x, str) else str(x)[:30])
def test_hook_domain_params(hook, expected_params):
    func = getattr(hooks, hook)
    sig = inspect.signature(func)
    param_names = set(sig.parameters.keys())
    for p in expected_params:
        assert p in param_names, f"{hook} missing param {p}"
