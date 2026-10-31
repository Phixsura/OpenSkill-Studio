from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bentoml import fleet_bentoml_status
def test_bml():
    r = fleet_bentoml_status([{"running": True, "bentos": 10, "requests_24h": 500000}])
    assert r["bentos"] == 10
    assert r["all_running"]
