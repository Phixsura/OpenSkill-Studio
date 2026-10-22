"""App notification service — 6 notification functions."""

import inspect
import pytest
from app.services import app_notifications

NOTIFIERS = [
    "notify_app_installed",
    "notify_app_uninstalled",
    "notify_review_submitted",
    "notify_review_decided",
    "notify_app_revoked",
    "notify_version_published",
]

@pytest.mark.parametrize("name", NOTIFIERS)
def test_exists(name):
    assert hasattr(app_notifications, name)

@pytest.mark.parametrize("name", NOTIFIERS)
def test_is_async(name):
    assert inspect.iscoroutinefunction(getattr(app_notifications, name))

@pytest.mark.parametrize("name", NOTIFIERS)
def test_requires_db(name):
    assert "db" in inspect.signature(getattr(app_notifications, name)).parameters

@pytest.mark.parametrize("name", NOTIFIERS)
def test_requires_app_id(name):
    assert "app_id" in inspect.signature(getattr(app_notifications, name)).parameters

def test_count():
    assert len(NOTIFIERS) == 6
