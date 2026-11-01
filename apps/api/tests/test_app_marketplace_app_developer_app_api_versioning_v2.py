from app.services.app_marketplace_app_developer_app_api_versioning_v2 import resolve_api_version, build_version_negotiation_response, compute_version_adoption

def test_url_version():
    r = resolve_api_version(accept_header=None, url_version="v2")
    assert r["version"] == "v2"
    assert r["source"] == "url"

def test_header_version():
    r = resolve_api_version(accept_header="application/vnd.openskill.v3+json", url_version=None)
    assert r["version"] == "v3"

def test_default():
    r = resolve_api_version(accept_header=None, url_version=None)
    assert r["version"] == "v1"

def test_negotiate_ok():
    r = build_version_negotiation_response(requested="v2", available=["v1", "v2"], deprecated=["v1"])
    assert r["status"] == 200

def test_negotiate_deprecated():
    r = build_version_negotiation_response(requested="v1", available=["v1", "v2"], deprecated=["v1"])
    assert r["headers"]["Deprecation"] == "true"

def test_negotiate_unavailable():
    r = build_version_negotiation_response(requested="v5", available=["v1", "v2"], deprecated=[])
    assert r["status"] == 406

def test_adoption():
    r = compute_version_adoption(requests_by_version={"v2": 8000, "v1": 2000})
    assert r[0]["version"] == "v2"
    assert r[0]["pct"] == 80.0
