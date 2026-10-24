from app.services.app_marketplace_app_app_app_app_app_app_app_traffic_mirror import TrafficMirror

def test_mirror():
    tm = TrafficMirror()
    tm.create_mirror("prod-api", "shadow-api")
    tm.create_mirror("prod-api", "canary-api")
    results = tm.mirror_request("prod-api")
    assert len(results) == 2
    assert tm.stats()["total_mirrored"] == 2

def test_pause():
    tm = TrafficMirror()
    tm.create_mirror("prod", "shadow")
    tm.pause("prod", "shadow")
    results = tm.mirror_request("prod")
    assert len(results) == 0
