"""Tests for App Geo Routing — regions, resolution, fallback."""

import pytest

from app.services.app_geo_routing import AppGeoRouting


class TestAddRegion:
    def test_add(self):
        g = AppGeoRouting()
        r = g.add_region("inst-1", "us-east", "US East", "https://us-east.api.com", ["US", "CA"])
        assert r.countries == ["US", "CA"]

    def test_duplicate(self):
        g = AppGeoRouting()
        g.add_region("inst-1", "us", "US", "https://us.api.com", ["US"])
        with pytest.raises(ValueError):
            g.add_region("inst-1", "us", "US2", "https://us2.api.com", ["US"])


class TestResolve:
    def test_resolve(self):
        g = AppGeoRouting()
        g.add_region("inst-1", "eu", "Europe", "https://eu.api.com", ["DE", "FR", "GB"])
        r = g.resolve("inst-1", "DE")
        assert r.region_id == "eu"

    def test_case_insensitive(self):
        g = AppGeoRouting()
        g.add_region("inst-1", "eu", "Europe", "https://eu.api.com", ["DE"])
        r = g.resolve("inst-1", "de")
        assert r.region_id == "eu"

    def test_default_fallback(self):
        g = AppGeoRouting(default_region="us")
        g.add_region("inst-1", "us", "US", "https://us.api.com", ["US"])
        r = g.resolve("inst-1", "ZZ")
        assert r.region_id == "us"

    def test_no_match(self):
        g = AppGeoRouting()
        g.add_region("inst-1", "us", "US", "https://us.api.com", ["US"])
        with pytest.raises(KeyError):
            g.resolve("inst-1", "ZZ")

    def test_request_count(self):
        g = AppGeoRouting()
        g.add_region("inst-1", "us", "US", "https://us.api.com", ["US"])
        g.resolve("inst-1", "US")
        g.resolve("inst-1", "US")
        r = g.list_regions("inst-1")[0]
        assert r.request_count == 2

    def test_disabled_skipped(self):
        g = AppGeoRouting()
        g.add_region("inst-1", "us", "US", "https://us.api.com", ["US"])
        g.disable_region("inst-1", "us")
        with pytest.raises(KeyError):
            g.resolve("inst-1", "US")


class TestIsolation:
    def test_cross_installation(self):
        g = AppGeoRouting()
        g.add_region("inst-1", "us", "US", "https://us.api.com", ["US"])
        with pytest.raises(KeyError):
            g.resolve("inst-2", "US")
