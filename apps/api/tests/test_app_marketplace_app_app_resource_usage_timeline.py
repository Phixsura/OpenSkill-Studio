from app.services.app_marketplace_app_app_resource_usage_timeline import build_usage_timeline

def test_timeline():
    data = [
        {"timestamp": "T1", "cpu": 30, "memory": 50},
        {"timestamp": "T2", "cpu": 60, "memory": 55},
        {"timestamp": "T3", "cpu": 45, "memory": 70},
    ]
    r = build_usage_timeline(data_points=data)
    assert r["total_points"] == 3
    assert r["stats"]["cpu"]["peak"] == 60
    assert r["stats"]["cpu"]["avg"] == 45.0
    assert r["stats"]["memory"]["current"] == 70

def test_empty():
    r = build_usage_timeline(data_points=[])
    assert r["total_points"] == 0
