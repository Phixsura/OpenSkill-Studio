from app.services.app_marketplace_app_user_growth_tracker import calculate_growth_metrics

def test_growing():
    periods = [
        {"period": "2026-08", "new_users": 500, "churned": 50, "total_users": 5000},
        {"period": "2026-09", "new_users": 600, "churned": 40, "total_users": 5560},
        {"period": "2026-10", "new_users": 700, "churned": 30, "total_users": 6230},
    ]
    r = calculate_growth_metrics(periods=periods)
    assert r["trend"] == "growing"
    assert r["current_total"] == 6230
    assert r["avg_growth_rate"] > 0

def test_empty():
    r = calculate_growth_metrics(periods=[])
    assert "error" in r
