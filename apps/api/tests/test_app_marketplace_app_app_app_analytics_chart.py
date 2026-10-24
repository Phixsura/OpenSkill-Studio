from app.services.app_marketplace_app_app_app_analytics_chart import build_chart_data

def test_chart():
    points = [
        {"date": "2026-01-01", "installs": 10},
        {"date": "2026-01-02", "installs": 25},
        {"date": "2026-01-03", "installs": 15},
        {"date": "2026-01-04", "installs": 30},
    ]
    r = build_chart_data(data_points=points, metric="installs")
    assert r["total"] == 80
    assert r["peak"] == 30
    assert r["peak_date"] == "2026-01-04"
    assert r["trend"] == "up"
    assert r["data_points"] == 4

def test_empty():
    r = build_chart_data(data_points=[])
    assert r["total"] == 0
    assert r["trend"] == "flat"
