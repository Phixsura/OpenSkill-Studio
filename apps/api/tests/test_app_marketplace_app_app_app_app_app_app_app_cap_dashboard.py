from app.services.app_marketplace_app_app_app_app_app_app_app_cap_dashboard import capacity_overview

def test_overview():
    r = capacity_overview([
        {"name": "cpu", "type": "compute", "capacity": 100, "used": 45},
        {"name": "memory", "type": "compute", "capacity": 64, "used": 58},
        {"name": "disk", "type": "storage", "capacity": 1000, "used": 300},
    ])
    assert r["resource_count"] == 3
    assert r["critical_count"] == 1  # memory 90.6%
    assert r["status"] == "critical"
