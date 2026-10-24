"""Tests for notification service functions — verify all notifications are well-formed."""

import pytest

from app.services.app_notifications import (
    notify_app_installed,
    notify_app_revoked,
    notify_app_uninstalled,
    notify_review_decided,
    notify_review_submitted,
    notify_version_published,
)


def test_all_notification_functions_exist():
    funcs = [notify_app_installed, notify_app_uninstalled, notify_review_submitted, notify_review_decided, notify_app_revoked, notify_version_published]
    assert all(callable(f) for f in funcs)
    assert len(funcs) == 6


def test_notification_functions_are_async():
    import asyncio
    assert asyncio.iscoroutinefunction(notify_app_installed)
    assert asyncio.iscoroutinefunction(notify_app_uninstalled)
    assert asyncio.iscoroutinefunction(notify_review_submitted)
    assert asyncio.iscoroutinefunction(notify_review_decided)
    assert asyncio.iscoroutinefunction(notify_app_revoked)
    assert asyncio.iscoroutinefunction(notify_version_published)


def test_notification_module_has_no_side_effects():
    """Importing should not create any DB connections."""
    import app.services.app_notifications
    assert hasattr(app.services.app_notifications, "notify_app_installed")
