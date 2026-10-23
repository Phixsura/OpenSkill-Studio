from app.services.app_marketplace_app_app_app_app_app_app_app_app_deps import check_dependencies

def test_all_ok():
    r = check_dependencies(
        [{"name": "auth", "version": "1.0"}, {"name": "webhooks", "version": "2.0"}],
        {"auth": "1.5", "webhooks": "2.1", "analytics": "3.0"})
    assert r["all_satisfied"]
    assert r["missing_count"] == 0

def test_missing():
    r = check_dependencies(
        [{"name": "auth"}, {"name": "missing_dep"}],
        {"auth": "1.0"})
    assert not r["all_satisfied"]
    assert "missing_dep" in r["missing"]
