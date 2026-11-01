"""Tests for App Webhook Secret Rotation — init, rotate, complete."""

import pytest

from app.services.app_webhook_secret_rotation import AppWebhookSecretRotation


class TestInit:
    def test_initialize(self):
        s = AppWebhookSecretRotation()
        raw = s.initialize_secret("inst-1")
        assert len(raw) > 20


class TestRotate:
    def test_rotate(self):
        s = AppWebhookSecretRotation()
        s.initialize_secret("inst-1")
        rotation, new_raw = s.rotate("inst-1", "r1", grace_seconds=60)
        assert rotation.in_grace_period is True
        assert len(new_raw) > 20

    def test_no_existing(self):
        s = AppWebhookSecretRotation()
        with pytest.raises(ValueError, match="No existing"):
            s.rotate("inst-1", "r1")


class TestComplete:
    def test_complete(self):
        s = AppWebhookSecretRotation()
        s.initialize_secret("inst-1")
        s.rotate("inst-1", "r1")
        r = s.complete("inst-1", "r1")
        assert r.completed is True
        assert r.in_grace_period is False


class TestIsolation:
    def test_cross(self):
        s = AppWebhookSecretRotation()
        s.initialize_secret("inst-1")
        s.rotate("inst-1", "r1")
        assert s.list_rotations("inst-2") == []
