"""Tests for App Endpoint Discovery — register, list, filter, tags."""

import pytest

from app.services.app_endpoint_discovery import AppEndpointDiscovery


class TestRegister:
    def test_register(self):
        d = AppEndpointDiscovery()
        ep = d.register_endpoint("inst-1", "GET", "/api/users", description="List users", tags=["users"])
        assert ep.method == "GET"
        assert ep.auth_required is True

    def test_replace(self):
        d = AppEndpointDiscovery()
        d.register_endpoint("inst-1", "GET", "/api/users", description="Old")
        d.register_endpoint("inst-1", "GET", "/api/users", description="New")
        assert d.endpoint_count("inst-1") == 1
        eps = d.list_endpoints("inst-1")
        assert eps[0].description == "New"


class TestList:
    def test_all(self):
        d = AppEndpointDiscovery()
        d.register_endpoint("inst-1", "GET", "/api/users")
        d.register_endpoint("inst-1", "POST", "/api/users")
        assert d.endpoint_count("inst-1") == 2

    def test_filter_tag(self):
        d = AppEndpointDiscovery()
        d.register_endpoint("inst-1", "GET", "/api/users", tags=["users"])
        d.register_endpoint("inst-1", "GET", "/api/orders", tags=["orders"])
        eps = d.list_endpoints("inst-1", tag="users")
        assert len(eps) == 1

    def test_exclude_deprecated(self):
        d = AppEndpointDiscovery()
        d.register_endpoint("inst-1", "GET", "/api/v1", deprecated=True)
        d.register_endpoint("inst-1", "GET", "/api/v2")
        eps = d.list_endpoints("inst-1", include_deprecated=False)
        assert len(eps) == 1


class TestTags:
    def test_get_tags(self):
        d = AppEndpointDiscovery()
        d.register_endpoint("inst-1", "GET", "/a", tags=["users", "admin"])
        d.register_endpoint("inst-1", "GET", "/b", tags=["orders"])
        assert d.get_tags("inst-1") == ["admin", "orders", "users"]


class TestCounts:
    def test_deprecated_count(self):
        d = AppEndpointDiscovery()
        d.register_endpoint("inst-1", "GET", "/old", deprecated=True)
        d.register_endpoint("inst-1", "GET", "/new")
        assert d.deprecated_count("inst-1") == 1


class TestIsolation:
    def test_cross_installation(self):
        d = AppEndpointDiscovery()
        d.register_endpoint("inst-1", "GET", "/api")
        assert d.endpoint_count("inst-2") == 0
