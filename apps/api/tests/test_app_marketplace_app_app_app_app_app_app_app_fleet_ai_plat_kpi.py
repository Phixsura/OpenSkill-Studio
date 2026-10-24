from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_kpi import fleet_ai_platform_kpi
def test_kpi():
    r = fleet_ai_platform_kpi([{"active": True, "kpis": 50, "green": 50, "red": 0}])
    assert r["green"] == 50
    assert r["on_track"]
