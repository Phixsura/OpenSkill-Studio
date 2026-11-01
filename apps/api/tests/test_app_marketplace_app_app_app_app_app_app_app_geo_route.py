from app.services.app_marketplace_app_app_app_app_app_app_app_geo_route import route_to_nearest, region_health

def test_route():
    r = route_to_nearest(48.8566, 2.3522, [  # Paris
        {"name": "eu-west", "lat": 53.3498, "lon": -6.2603, "status": "healthy", "endpoint": "eu.api.com"},
        {"name": "us-east", "lat": 39.0438, "lon": -77.4874, "status": "healthy", "endpoint": "us.api.com"},
    ])
    assert r["routed"]
    assert r["region"] == "eu-west"

def test_skip_unhealthy():
    r = route_to_nearest(40.0, -74.0, [
        {"name": "us-east", "lat": 39.0, "lon": -77.0, "status": "unhealthy"},
        {"name": "eu-west", "lat": 53.0, "lon": -6.0, "status": "healthy", "endpoint": "eu.api.com"},
    ])
    assert r["region"] == "eu-west"

def test_health():
    r = region_health([{"status": "healthy"}, {"status": "healthy"}, {"status": "unhealthy"}])
    assert r["healthy"] == 2
