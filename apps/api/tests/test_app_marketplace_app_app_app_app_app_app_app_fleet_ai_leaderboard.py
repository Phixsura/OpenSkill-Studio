from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_leaderboard import fleet_ai_leaderboard
def test_lb():
    r = fleet_ai_leaderboard([{"active": True, "models": 200, "benchmarks": 50, "submissions_24h": 1000}])
    assert r["models"] == 200
    assert r["competitive"]
