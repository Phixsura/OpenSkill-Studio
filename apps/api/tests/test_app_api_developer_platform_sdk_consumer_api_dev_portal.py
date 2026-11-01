"""Tests for Consumer API Developer Portal service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_dev_portal import (
    DeveloperPortal, PortalSection, GettingStartedStep,
)


class TestDeveloperPortal:
    def test_add_section(self):
        svc = DeveloperPortal()
        result = svc.add_section(PortalSection("s1", "Authentication", "How to authenticate", "guide"))
        assert result["category"] == "guide"

    def test_getting_started(self):
        svc = DeveloperPortal()
        svc.add_getting_started_step(GettingStartedStep("gs1", "Create Account", "Sign up", order=1))
        svc.add_getting_started_step(GettingStartedStep("gs2", "Get API Key", "Generate key", order=2))
        portal = svc.get_portal()
        assert len(portal["getting_started"]) == 2
        assert portal["getting_started"][0]["title"] == "Create Account"

    def test_quicklinks(self):
        svc = DeveloperPortal()
        svc.add_quicklink("API Docs", "https://docs.example.com", "📖")
        svc.add_quicklink("Status", "https://status.example.com", "🟢")
        portal = svc.get_portal()
        assert len(portal["quicklinks"]) == 2

    def test_get_section(self):
        svc = DeveloperPortal()
        svc.add_section(PortalSection("s1", "Auth", "How to auth"))
        section = svc.get_section("s1")
        assert section is not None
        assert section["title"] == "Auth"

    def test_search(self):
        svc = DeveloperPortal()
        svc.add_section(PortalSection("s1", "Authentication Guide", "OAuth flow"))
        svc.add_section(PortalSection("s2", "Rate Limiting", "Limits info"))
        results = svc.search("auth")
        assert len(results) == 1

    def test_categories(self):
        svc = DeveloperPortal()
        svc.add_section(PortalSection("s1", "Auth", "x", "guide"))
        svc.add_section(PortalSection("s2", "Errors", "y", "reference"))
        portal = svc.get_portal()
        assert "guide" in portal["categories"]
        assert "reference" in portal["categories"]

    def test_stats(self):
        svc = DeveloperPortal()
        svc.add_section(PortalSection("s1", "A", "x", "guide"))
        svc.add_section(PortalSection("s2", "B", "y", "tutorial"))
        svc.add_getting_started_step(GettingStartedStep("gs1", "Step 1", "Do this"))
        stats = svc.get_stats()
        assert stats["total_sections"] == 2
        assert stats["getting_started_steps"] == 1

    def test_duplicate_section(self):
        svc = DeveloperPortal()
        svc.add_section(PortalSection("s1", "A", "x"))
        with pytest.raises(ValueError):
            svc.add_section(PortalSection("s1", "B", "y"))

    def test_duplicate_step(self):
        svc = DeveloperPortal()
        svc.add_getting_started_step(GettingStartedStep("gs1", "A", "x"))
        with pytest.raises(ValueError):
            svc.add_getting_started_step(GettingStartedStep("gs1", "B", "y"))

    def test_not_found(self):
        svc = DeveloperPortal()
        assert svc.get_section("missing") is None

    def test_isolation(self):
        a, b = DeveloperPortal(), DeveloperPortal()
        a.add_section(PortalSection("s1", "A", "x"))
        assert b.get_stats()["total_sections"] == 0
