"""Notification function return type annotations."""

import inspect
import pytest
from app.services.app_notifications import (
    notify_app_installed, notify_app_uninstalled, notify_review_submitted,
    notify_review_decided, notify_app_revoked, notify_version_published,
)

FUNCS = [notify_app_installed, notify_app_uninstalled, notify_review_submitted,
         notify_review_decided, notify_app_revoked, notify_version_published]

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_is_coroutine(func):
    assert inspect.iscoroutinefunction(func)
