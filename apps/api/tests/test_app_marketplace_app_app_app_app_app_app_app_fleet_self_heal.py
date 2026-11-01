from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_self_heal import fleet_self_healing
def test_heal():
    r = fleet_self_healing([{"auto_recovered": True}] * 8 + [{"auto_recovered": False}] * 2)
    assert r["auto_recovered"] == 8
    assert r["automation_rate"] == 80.0
    assert r["mature"]
