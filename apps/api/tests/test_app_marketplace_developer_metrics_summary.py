from app.services.app_marketplace_developer_metrics_summary import build_metrics_summary

def test_summary():
    apps = [
        {"install_count": 500, "api_calls": 10000, "avg_rating": 4.5, "revenue_cents": 9900, "status": "published"},
        {"install_count": 200, "api_calls": 5000, "avg_rating": 4.0, "revenue_cents": 0, "status": "draft"},
    ]
    r = build_metrics_summary(apps=apps)
    assert len(r["metrics"]) == 5
    assert r["metrics"][0]["value"] == 700
    assert r["metrics"][4]["value"] == 1  # only 1 published

def test_empty():
    r = build_metrics_summary(apps=[])
    assert r["metrics"][0]["value"] == 0
