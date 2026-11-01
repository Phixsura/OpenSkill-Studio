from app.services.app_marketplace_app_app_app_app_app_app_app_traffic_split import split_traffic, validate_splits

def test_split():
    splits = [{"version": "v1", "pct": 90}, {"version": "v2", "pct": 10}]
    results = [split_traffic(f"user-{i}", splits)["version"] for i in range(1000)]
    v1_count = results.count("v1")
    assert 800 < v1_count < 980  # roughly 90%

def test_validate():
    r = validate_splits([{"version": "v1", "pct": 80}, {"version": "v2", "pct": 20}])
    assert r["valid"]
    r2 = validate_splits([{"version": "v1", "pct": 80}])
    assert not r2["valid"]
