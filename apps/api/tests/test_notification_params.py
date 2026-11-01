"""Notification function parameter validation."""

import inspect
import pytest
from app.services.app_notifications import (
    notify_app_installed, notify_app_uninstalled, notify_review_submitted,
    notify_review_decided, notify_app_revoked, notify_version_published,
)

NOTIFIERS_WITH_PARAMS = [
    (notify_app_installed, ["db", "app_id", "org_id"]),
    (notify_app_uninstalled, ["db", "app_id", "org_id"]),
    (notify_review_submitted, ["db", "app_id"]),
    (notify_review_decided, ["db", "app_id"]),
    (notify_app_revoked, ["db", "app_id"]),
    (notify_version_published, ["db", "app_id"]),
]

@pytest.mark.parametrize("func,required_params", NOTIFIERS_WITH_PARAMS,
    ids=lambda x: x.__name__ if callable(x) else str(x)[:30])
def test_required_params(func, required_params):
    params = set(inspect.signature(func).parameters.keys())
    for p in required_params:
        assert p in params, f"{func.__name__} missing param: {p}"
