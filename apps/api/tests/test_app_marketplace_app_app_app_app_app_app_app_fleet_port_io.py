from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_port_io import fleet_port_io
def test_port():
    r = fleet_port_io([{"entities": 100, "self_service_actions": 20}] * 10)
    assert r["entities"] == 1000
    assert r["mature"]
