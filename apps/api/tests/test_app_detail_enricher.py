from app.services.app_detail_enricher import enrich_app_detail

def test_basic():
    app = {"id": "a1", "name": "X", "manifest": {"permissions": ["read:cohorts"], "sandbox": {"runtime": "python3.12"}}}
    r = enrich_app_detail(app, executions=100, errors=5, install_count=50)
    assert r["health_score"] == 95
    assert r["install_count"] == 50
    assert r["has_sandbox"] is True
    assert r["permission_count"] == 1

def test_no_manifest():
    r = enrich_app_detail({"id": "a"})
    assert r["health_score"] == 100
    assert r["has_sandbox"] is False

def test_with_ui():
    app = {"manifest": {"ui_extensions": [{"surface": "dashboard_card"}]}}
    r = enrich_app_detail(app)
    assert r["has_ui"] is True
