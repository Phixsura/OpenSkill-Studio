"""Tests for Consumer API Maintenance Mode service."""
from app.services.app_api_developer_platform_sdk_consumer_api_maintenance_mode import MaintenanceModeManager


class TestMaintenanceModeManager:
    def test_enable_disable(self):
        svc = MaintenanceModeManager()
        svc.enable("Upgrading database", "2024-01-15T04:00:00Z")
        assert svc.is_maintenance() is True
        svc.disable()
        assert svc.is_maintenance() is False

    def test_check_access_not_maintenance(self):
        svc = MaintenanceModeManager()
        result = svc.check_access()
        assert result["allowed"] is True

    def test_check_access_blocked(self):
        svc = MaintenanceModeManager()
        svc.enable("Down for maintenance")
        result = svc.check_access()
        assert result["allowed"] is False
        assert result["message"] == "Down for maintenance"

    def test_bypass_key(self):
        svc = MaintenanceModeManager()
        svc.enable()
        key_result = svc.generate_bypass_key()
        key = key_result["bypass_key"]
        result = svc.check_access(bypass_key=key)
        assert result["allowed"] is True
        assert result["reason"] == "bypass_key"

    def test_revoke_bypass_key(self):
        svc = MaintenanceModeManager()
        svc.enable()
        key = svc.generate_bypass_key()["bypass_key"]
        svc.revoke_bypass_key(key)
        result = svc.check_access(bypass_key=key)
        assert result["allowed"] is False

    def test_allowed_ip(self):
        svc = MaintenanceModeManager()
        svc.enable()
        svc.add_allowed_ip("10.0.0.1")
        result = svc.check_access(ip="10.0.0.1")
        assert result["allowed"] is True
        assert result["reason"] == "allowed_ip"

    def test_remove_allowed_ip(self):
        svc = MaintenanceModeManager()
        svc.add_allowed_ip("10.0.0.1")
        svc.remove_allowed_ip("10.0.0.1")
        svc.enable()
        result = svc.check_access(ip="10.0.0.1")
        assert result["allowed"] is False

    def test_get_status(self):
        svc = MaintenanceModeManager()
        svc.enable("Upgrade", "2024-01-15T04:00Z")
        svc.generate_bypass_key()
        svc.add_allowed_ip("10.0.0.1")
        status = svc.get_status()
        assert status["enabled"] is True
        assert status["bypass_keys"] == 1
        assert status["allowed_ips"] == 1

    def test_history(self):
        svc = MaintenanceModeManager()
        svc.enable()
        svc.disable()
        history = svc.get_history()
        assert len(history) == 2
        assert history[0]["action"] == "enabled"
        assert history[1]["action"] == "disabled"

    def test_isolation(self):
        a, b = MaintenanceModeManager(), MaintenanceModeManager()
        a.enable()
        assert b.is_maintenance() is False
