from app.services.app_marketplace_app_app_app_app_app_app_app_avail_zones import check_zone_health

def test_zones():
    r = check_zone_health([
        {"name": "us-east-1a", "region": "us-east-1", "status": "healthy"},
        {"name": "us-east-1b", "region": "us-east-1", "status": "healthy"},
        {"name": "eu-west-1a", "region": "eu-west-1", "status": "degraded"},
    ])
    assert r["total_zones"] == 3
    assert r["healthy"] == 2
    assert r["regions"] == 2
    assert r["multi_az"]
    assert not r["all_healthy"]
