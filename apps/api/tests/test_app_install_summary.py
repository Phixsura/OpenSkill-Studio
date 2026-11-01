from app.services.app_install_summary import compute_install_summary

def test_basic():
    s = compute_install_summary([{"status": "active", "category": "connector"}, {"status": "active", "category": "connector"}, {"status": "uninstalled", "category": "automation"}])
    assert s["active"] == 2
    assert s["total"] == 3
    assert s["by_category"]["connector"] == 2

def test_empty():
    s = compute_install_summary([])
    assert s["total"] == 0
