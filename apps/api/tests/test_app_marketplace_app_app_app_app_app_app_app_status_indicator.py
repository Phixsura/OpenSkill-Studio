from app.services.app_marketplace_app_app_app_app_app_app_app_status_indicator import get_indicator, aggregate_status

def test_indicator():
    r = get_indicator("operational")
    assert r["icon"] == "🟢"
    assert r["color"] == "green"

def test_aggregate():
    r = aggregate_status([
        {"name": "API", "status": "operational"},
        {"name": "DB", "status": "degraded"},
        {"name": "Cache", "status": "operational"},
    ])
    assert r["overall"]["status"] == "degraded"
    assert r["operational_count"] == 2
    assert r["total"] == 3
