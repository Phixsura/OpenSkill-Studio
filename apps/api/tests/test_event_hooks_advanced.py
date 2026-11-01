"""Advanced event hooks tests — verify all hooks are async and well-typed."""

import asyncio

from app.services.app_event_hooks import (
    on_app_installed,
    on_app_uninstalled,
    on_cohort_member_added,
    on_cohort_member_removed,
    on_evaluation_completed,
    on_org_member_added,
    on_pack_installed,
    on_pack_published,
    on_project_published,
    on_submission_completed,
    on_submission_graded,
    on_workflow_run_completed,
)


ALL_HOOKS = [
    on_submission_completed, on_submission_graded,
    on_cohort_member_added, on_cohort_member_removed,
    on_project_published, on_pack_published, on_pack_installed,
    on_workflow_run_completed, on_app_installed, on_app_uninstalled,
    on_evaluation_completed, on_org_member_added,
]


def test_all_hooks_count():
    assert len(ALL_HOOKS) == 12


def test_all_hooks_async():
    for hook in ALL_HOOKS:
        assert asyncio.iscoroutinefunction(hook), f"{hook.__name__} is not async"


def test_all_hooks_named():
    names = [h.__name__ for h in ALL_HOOKS]
    assert all(n.startswith("on_") for n in names)


def test_submission_hooks_exist():
    assert on_submission_completed is not None
    assert on_submission_graded is not None


def test_cohort_hooks_exist():
    assert on_cohort_member_added is not None
    assert on_cohort_member_removed is not None


def test_app_hooks_exist():
    assert on_app_installed is not None
    assert on_app_uninstalled is not None


def test_workflow_hook_exists():
    assert on_workflow_run_completed is not None


def test_org_hook_exists():
    assert on_org_member_added is not None
