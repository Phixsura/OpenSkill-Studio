from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dependabot import fleet_dependabot_status
def test_dep():
    r = fleet_dependabot_status([{"dependabot_enabled": True, "security_alerts": 3, "auto_merged_30d": 10}])
    assert r["security_alerts"] == 3
    assert not r["secure"]
