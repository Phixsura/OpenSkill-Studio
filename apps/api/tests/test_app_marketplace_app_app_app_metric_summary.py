from app.services.app_marketplace_app_app_app_metric_summary import build_metric_summary

def test_healthy():
    app = {"name": "SuperApp", "installs": 5000, "active_users": 3000,
           "api_calls": 100000, "error_count": 50, "avg_rating": 4.8}
    r = build_metric_summary(app=app)
    assert len(r["kpis"]) == 6
    assert r["health_grade"] in ("A", "B")
    assert r["app_name"] == "SuperApp"

def test_poor():
    app = {"name": "BadApp", "installs": 100, "active_users": 5,
           "api_calls": 1000, "error_count": 200, "avg_rating": 2.0}
    r = build_metric_summary(app=app)
    assert r["health_grade"] in ("C", "F")
