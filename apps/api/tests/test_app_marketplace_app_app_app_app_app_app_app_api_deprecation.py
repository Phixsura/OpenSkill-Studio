from app.services.app_marketplace_app_app_app_app_app_app_app_api_deprecation import (
    deprecate_endpoint, check_deprecated_usage, migration_guide,
)

def test_deprecate():
    r = deprecate_endpoint("/api/v1/users", "GET", "2025-06-01",
                             replacement="/api/v2/users", reason="v2 available")
    assert r["status"] == "deprecated"

def test_usage():
    deps = [deprecate_endpoint("/v1/a", "GET", "2025-01-01"),
            deprecate_endpoint("/v1/b", "POST", "2025-01-01")]
    r = check_deprecated_usage(deps, {"GET /v1/a": 500, "POST /v1/b": 0})
    assert r["deprecated_in_use"] == 1
    assert r["total_calls_to_deprecated"] == 500

def test_guide():
    d = deprecate_endpoint("/v1/x", "GET", "2025-06-01", "/v2/x", "new version")
    r = migration_guide(d)
    assert len(r["steps"]) == 3
    assert r["to"] == "/v2/x"
