"""Tests for App API OAuth Client — register, verify, deactivate."""

import pytest
from app.services.app_api_oauth_client import AppAPIOAuthClient


class TestRegister:
    def test_register(self):
        o = AppAPIOAuthClient()
        client, secret = o.register("inst-1", "My App", ["https://app.com/callback"])
        assert client.client_id.startswith("oc_")
        assert len(secret) > 20

    def test_invalid_grant(self):
        o = AppAPIOAuthClient()
        with pytest.raises(ValueError, match="Invalid grant"):
            o.register("inst-1", "App", ["https://a.com"], ["bogus"])


class TestVerify:
    def test_valid(self):
        o = AppAPIOAuthClient()
        client, secret = o.register("inst-1", "App", ["https://a.com"])
        assert o.verify_secret("inst-1", client.client_id, secret) is True

    def test_invalid(self):
        o = AppAPIOAuthClient()
        client, _ = o.register("inst-1", "App", ["https://a.com"])
        assert o.verify_secret("inst-1", client.client_id, "wrong") is False

    def test_deactivated(self):
        o = AppAPIOAuthClient()
        client, secret = o.register("inst-1", "App", ["https://a.com"])
        o.deactivate("inst-1", client.client_id)
        assert o.verify_secret("inst-1", client.client_id, secret) is False


class TestIsolation:
    def test_cross(self):
        o = AppAPIOAuthClient()
        o.register("inst-1", "App", ["https://a.com"])
        assert o.list_clients("inst-2") == []
