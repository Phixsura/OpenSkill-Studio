from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_timeline import build_timeline

def test_timeline():
    r = build_timeline([
        {"timestamp": 1, "healthy": 8, "total": 10},
        {"timestamp": 2, "healthy": 9, "total": 10},
        {"timestamp": 3, "healthy": 10, "total": 10},
    ])
    assert r["trend"] == "improving"
    assert r["current_pct"] == 100.0
    assert r["data_points"] == 3

def test_declining():
    r = build_timeline([
        {"timestamp": 1, "healthy": 10, "total": 10},
        {"timestamp": 2, "healthy": 7, "total": 10},
    ])
    assert r["trend"] == "declining"
