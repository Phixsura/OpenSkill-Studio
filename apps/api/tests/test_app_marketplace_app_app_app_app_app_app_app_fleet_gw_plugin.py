from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gw_plugin import fleet_gw_plugins
def test_plugins():
    r = fleet_gw_plugins([{"enabled": True}, {"enabled": True, "deprecated": True}, {"enabled": False}])
    assert r["active"] == 2
    assert r["deprecated"] == 1
    assert not r["healthy"]
