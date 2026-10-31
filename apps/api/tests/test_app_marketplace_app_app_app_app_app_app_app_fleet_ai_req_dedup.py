from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_req_dedup import fleet_ai_request_dedup
def test_rd():
    r = fleet_ai_request_dedup([{"active": True, "requests_24h": 10000000, "deduped": 2000000}])
    assert r["savings_pct"] == 20.0
    assert r["saving"]
