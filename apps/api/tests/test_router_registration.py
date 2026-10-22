"""Verify all developer platform routers are registered."""

import pytest
from app.api.v1.router import api_v1_router

EXPECTED_PREFIXES = [
    "/developer-accounts",
    "/apps",
    "/installations",
    "/marketplace",
    "/oauth",
]

@pytest.mark.parametrize("prefix", EXPECTED_PREFIXES)
def test_router_prefix_registered(prefix):
    all_paths = [r.path for r in api_v1_router.routes if hasattr(r, "path")]
    matched = [p for p in all_paths if prefix in p]
    assert len(matched) > 0, f"No routes with prefix {prefix}"

def test_minimum_route_count():
    """Developer platform should register many routes."""
    all_paths = [r.path for r in api_v1_router.routes if hasattr(r, "path")]
    # At least 50 routes across all dev platform endpoints
    assert len(all_paths) >= 50

def test_no_duplicate_routes():
    """No exact duplicate path+method combos."""
    seen = set()
    for route in api_v1_router.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            for method in route.methods:
                key = (route.path, method)
                assert key not in seen, f"Duplicate: {method} {route.path}"
                seen.add(key)
