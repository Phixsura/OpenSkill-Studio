from app.services.app_marketplace_app_app_app_app_app_app_app_util_heatmap import build_heatmap

def test_heatmap():
    r = build_heatmap(["api", "db"], 3, {"api": [40, 85, 60], "db": [30, 50, 90]})
    assert len(r["cells"]) == 6
    assert r["hotspot_count"] == 2  # 85, 90
    assert r["max_value"] == 90.0
    assert r["avg_utilization"] > 0
