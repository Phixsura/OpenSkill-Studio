from app.services.app_org_dashboard import build_org_dashboard

INSTALLS = [{"status": "active", "category": "connector"}, {"status": "active", "category": "connector"},
            {"status": "uninstalled", "category": "automation"}]

def test_basic():
    d = build_org_dashboard(installations=INSTALLS, total_executions=1000, total_errors=10)
    assert d["active"] == 2
    assert d["total_installed"] == 3
    assert d["error_rate"] == 1.0
    assert d["health"] == "healthy"

def test_categories():
    d = build_org_dashboard(installations=INSTALLS)
    assert d["by_category"]["connector"] == 2

def test_empty():
    d = build_org_dashboard(installations=[])
    assert d["active"] == 0
    assert d["health"] == "healthy"
