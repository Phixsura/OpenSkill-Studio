from app.services.app_marketplace_app_app_app_app_app_app_app_change_impact import score_change, batch_score

def test_critical():
    r = score_change({"breaking": True, "consumer_count": 200, "env": "production"})
    assert r["risk"] == "critical"
    assert r["score"] >= 70

def test_low():
    r = score_change({"breaking": False, "consumer_count": 2})
    assert r["risk"] == "low"

def test_batch():
    r = batch_score([
        {"breaking": True, "consumer_count": 200},
        {"breaking": False, "consumer_count": 5},
    ])
    assert r["critical"] == 1
    assert r["total"] == 2
