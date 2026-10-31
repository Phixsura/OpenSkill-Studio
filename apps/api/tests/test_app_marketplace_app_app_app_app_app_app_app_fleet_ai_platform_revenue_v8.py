from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_revenue_v8 import fleet_ai_revenue_v8
def test_rv8():
    r = fleet_ai_revenue_v8([{"active": True, "mrr_usd": 100000000, "ndr_pct": 140, "margin_pct": 80}])
    assert r["mrr"] == 100000000
    assert r["efficient"]
