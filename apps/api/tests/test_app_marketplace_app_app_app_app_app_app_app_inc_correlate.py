from app.services.app_marketplace_app_app_app_app_app_app_app_inc_correlate import correlate_incidents, suggest_root_cause

def test_correlate():
    r = correlate_incidents([
        {"id": "inc1", "tags": ["database", "timeout"]},
        {"id": "inc2", "tags": ["database", "connection"]},
        {"id": "inc3", "tags": ["network"]},
    ])
    assert r["has_correlations"]
    assert r["correlations"][0]["tag"] == "database"
    assert r["correlations"][0]["count"] == 2

def test_root_cause():
    r = suggest_root_cause({"tag": "database", "count": 5})
    assert r["confidence"] == "high"
    assert "database" in r["suggestion"]
