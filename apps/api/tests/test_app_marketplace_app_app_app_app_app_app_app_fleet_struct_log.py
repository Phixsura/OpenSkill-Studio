from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_struct_log import fleet_structured_logging
def test_log():
    r = fleet_structured_logging([{"structured": True, "format": "json"}, {"structured": True, "format": "json"}, {"structured": False}])
    assert r["structured"] == 2
    assert r["json"] == 2
    assert not r["mature"]
