from app.services.app_marketplace_app_app_app_app_app_app_app_dep_staleness import check_staleness

def test_staleness():
    r = check_staleness([
        {"name": "react", "version": "18.2", "latest": "18.3", "age_days": 200},
        {"name": "next", "version": "15.0", "latest": "15.0", "age_days": 30},
        {"name": "lodash", "version": "4.17.20", "latest": "4.17.21", "age_days": 365},
    ], max_age_days=180)
    assert r["stale_count"] == 2
    assert r["current"] == 1
    assert r["stale"][0]["name"] == "lodash"
    assert r["staleness_pct"] == 66.7
