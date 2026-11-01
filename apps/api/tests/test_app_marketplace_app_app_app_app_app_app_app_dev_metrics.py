from app.services.app_marketplace_app_app_app_app_app_app_app_dev_metrics import compute_dev_metrics

def test_metrics():
    r = compute_dev_metrics(developer_id="dev1", apps=[
        {"installs": 50000, "reviews": 200, "rating": 4.8, "api_calls": 1000000},
        {"installs": 30000, "reviews": 80, "rating": 4.2, "api_calls": 500000},
    ], support_tickets=12, avg_response_hours=3.5)
    assert r["app_count"] == 2
    assert r["total_installs"] == 80000
    assert r["avg_rating"] == 4.5
    assert r["support_grade"] == "A"
    assert r["quality_score"] > 0
    assert r["api_display"] == "1,500,000"
