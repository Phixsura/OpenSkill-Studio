from app.services.app_marketplace_app_app_app_app_app_app_app_svc_status_agg import aggregate_status

def test_aggregate():
    r = aggregate_status([
        {"service": "api", "status": "healthy"},
        {"service": "api", "status": "healthy"},
        {"service": "db", "status": "healthy"},
        {"service": "db", "status": "down"},
    ])
    assert r["healthy"] == 1
    assert r["services"][0]["consensus"] == "healthy"
    assert r["services"][1]["consensus"] == "down"
