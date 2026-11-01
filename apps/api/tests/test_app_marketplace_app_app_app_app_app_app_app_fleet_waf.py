from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_waf import fleet_waf_status
def test_waf():
    r = fleet_waf_status([{"blocked": 500, "allowed": 9500}, {"blocked": 200, "allowed": 4800}])
    assert r["blocked"] == 700
    assert r["block_rate_pct"] == 4.67
