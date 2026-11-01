from app.services.app_marketplace_app_api_deprecation_manager import deprecate_endpoint, build_deprecation_headers, check_sunset_status

def test_deprecate():
    d = deprecate_endpoint(path="/api/v1/users", method="GET", sunset_date="2027-01-01", replacement="/api/v2/users")
    assert d["status"] == "deprecated"
    assert d["replacement"] == "/api/v2/users"

def test_headers():
    ep = {"deprecated_at": "2026-06-01", "sunset_date": "2027-01-01", "replacement": "/v2/users"}
    h = build_deprecation_headers(endpoint=ep)
    assert "Deprecation" in h
    assert "Sunset" in h
    assert "successor-version" in h["Link"]

def test_no_replacement():
    ep = {"deprecated_at": "2026-06-01", "sunset_date": "2027-01-01", "replacement": None}
    h = build_deprecation_headers(endpoint=ep)
    assert "Link" not in h

def test_sunset():
    eps = [{"sunset_date": "2020-01-01"}, {"sunset_date": "2030-01-01"}]
    r = check_sunset_status(endpoints=eps)
    assert r["expired"] == 1
    assert r["needs_cleanup"]
