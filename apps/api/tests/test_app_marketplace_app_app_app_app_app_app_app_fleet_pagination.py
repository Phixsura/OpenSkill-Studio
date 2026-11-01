from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pagination import fleet_pagination
def test_pagination():
    r = fleet_pagination([{"supports_pagination": True, "pagination_type": "cursor"}, {"supports_pagination": True, "pagination_type": "offset"}, {"supports_pagination": False}])
    assert r["paginated"] == 2
    assert r["cursor_based"] == 1
    assert r["unpaginated"] == 1
