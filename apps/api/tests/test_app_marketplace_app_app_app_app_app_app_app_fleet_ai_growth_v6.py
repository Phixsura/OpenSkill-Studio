from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_growth_v6 import fleet_ai_growth_v6
def test_gv6():
    r = fleet_ai_growth_v6([{"active": True, "mau": 5000000, "arr_usd": 200000000, "growth_pct": 40, "ndr_pct": 140}])
    assert r["mau"] == 5000000
    assert r["scaling"]
