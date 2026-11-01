from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_waf_engine_v9 import fleet_waf_engine_v9
def test_waf_v9():
    r = fleet_waf_engine_v9([{"blocked": 500, "allowed": 10000, "false_positives": 0}])
    assert r["blocked"] == 500
    assert r["healthy"]
