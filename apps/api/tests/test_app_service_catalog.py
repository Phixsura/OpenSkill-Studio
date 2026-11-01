"""Tests for App Service Catalog — register, health, categories."""

import pytest

from app.services.app_service_catalog import AppServiceCatalog


class TestRegister:
    def test_register(self):
        c = AppServiceCatalog()
        s = c.register("inst-1", "auth", "Auth Service", "Handles authentication", "team-platform", category="core")
        assert s.service_id == "auth"
        assert s.health == "healthy"

    def test_missing_owner(self):
        c = AppServiceCatalog()
        with pytest.raises(ValueError):
            c.register("inst-1", "auth", "Auth", "Desc", "")


class TestHealth:
    def test_update(self):
        c = AppServiceCatalog()
        c.register("inst-1", "auth", "Auth", "Desc", "team")
        s = c.update_health("inst-1", "auth", "degraded")
        assert s.health == "degraded"

    def test_invalid_health(self):
        c = AppServiceCatalog()
        c.register("inst-1", "auth", "Auth", "Desc", "team")
        with pytest.raises(ValueError):
            c.update_health("inst-1", "auth", "broken")


class TestList:
    def test_all(self):
        c = AppServiceCatalog()
        c.register("inst-1", "auth", "Auth", "Desc", "team", category="core")
        c.register("inst-1", "billing", "Billing", "Desc", "team", category="finance")
        assert c.service_count("inst-1") == 2

    def test_filter_category(self):
        c = AppServiceCatalog()
        c.register("inst-1", "auth", "Auth", "Desc", "team", category="core")
        c.register("inst-1", "billing", "Billing", "Desc", "team", category="finance")
        svcs = c.list_services("inst-1", category="core")
        assert len(svcs) == 1

    def test_categories(self):
        c = AppServiceCatalog()
        c.register("inst-1", "a", "A", "D", "t", category="core")
        c.register("inst-1", "b", "B", "D", "t", category="data")
        assert c.get_categories("inst-1") == ["core", "data"]


class TestIsolation:
    def test_cross_installation(self):
        c = AppServiceCatalog()
        c.register("inst-1", "auth", "Auth", "Desc", "team")
        assert c.service_count("inst-2") == 0
