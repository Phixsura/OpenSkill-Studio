from app.services.app_marketplace_app_app_app_app_app_app_app_infra_overview import build_infra_overview

def test_overview():
    r = build_infra_overview({
        "compute": {"nodes": 20, "cpu_cores": 160, "memory_gb": 640, "cost": 8000, "healthy": True},
        "storage": {"total_tb": 50, "cost": 2000, "healthy": True},
        "network": {"bandwidth_gbps": 10, "cost": 500, "healthy": True},
    })
    assert r["total_cost"] == 10500
    assert r["health"] == "healthy"
    assert r["compute"]["nodes"] == 20
