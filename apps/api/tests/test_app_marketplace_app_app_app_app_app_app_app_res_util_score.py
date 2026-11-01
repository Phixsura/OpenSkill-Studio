from app.services.app_marketplace_app_app_app_app_app_app_app_res_util_score import score_utilization

def test_optimal():
    r = score_utilization([{"name": "api", "cpu_pct": 55, "memory_pct": 55}])
    assert r["scores"][0]["status"] == "optimal"
    assert r["scores"][0]["score"] == 100

def test_underused():
    r = score_utilization([{"name": "idle", "cpu_pct": 5, "memory_pct": 10}])
    assert r["scores"][0]["status"] == "underused"
    assert r["scores"][0]["score"] < 50
