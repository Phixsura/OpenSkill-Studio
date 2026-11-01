from app.services.app_marketplace_app_app_app_app_app_app_app_release_train import create_train, advance_service

def test_create():
    t = create_train("Q4 Release", [
        {"name": "api", "version": "3.0", "status": "ready"},
        {"name": "web", "version": "3.0", "status": "pending"},
        {"name": "worker", "version": "3.0", "status": "pending"},
    ], "2024-12-15")
    assert t["total"] == 3
    assert t["ready"] == 1
    assert t["pct_ready"] == 33

def test_advance():
    t = create_train("v2", [
        {"name": "api", "version": "2.0", "status": "pending"},
        {"name": "web", "version": "2.0", "status": "pending"},
    ], "2024-11-01")
    advance_service(t, "api", "ready")
    assert t["ready"] == 1
    advance_service(t, "web", "ready")
    assert t["all_ready"]
    assert t["pct_ready"] == 100
