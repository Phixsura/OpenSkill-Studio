from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_response_header_v9 import fleet_api_response_header_v9
def test_arh2_v9():
    r = fleet_api_response_header_v9([{"csp": True, "hsts": True, "x_frame_options": True}])
    assert r["hsts"] == 1
    assert r["healthy"]
