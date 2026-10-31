from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_retry_stats import analyze_retries

def test_analyze():
    r = analyze_retries([
        {"source": "api", "destination": "db", "is_retry": False, "status": 200},
        {"source": "api", "destination": "db", "is_retry": True, "status": 200},
        {"source": "api", "destination": "db", "is_retry": True, "status": 500},
        {"source": "web", "destination": "api", "is_retry": False, "status": 200},
    ])
    assert r["total_retries"] == 2
    assert r["pairs_with_retries"] == 1
    db_pair = [p for p in r["pairs"] if "db" in p["pair"]][0]
    assert db_pair["retries"] == 2
    assert db_pair["retry_success_rate"] == 50.0
