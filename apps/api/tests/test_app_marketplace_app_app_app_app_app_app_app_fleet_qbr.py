from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_qbr import fleet_qbr_summary
def test_qbr():
    r = fleet_qbr_summary({"name": "Q4", "revenue_target": 100000, "revenue_actual": 120000})
    assert r["achievement_pct"] == 120.0
    assert r["target_hit"]
