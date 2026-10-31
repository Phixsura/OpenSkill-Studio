from app.services.app_marketplace_app_app_app_app_app_app_app_log_retention import evaluate_retention, storage_projection

def test_retention():
    r = evaluate_retention([
        {"type": "access", "age_days": 10, "size_mb": 100},
        {"type": "access", "age_days": 100, "size_mb": 500},
        {"type": "error", "age_days": 50, "size_mb": 50},
        {"type": "error", "age_days": 100, "size_mb": 200},
    ], policies={"access": 30, "error": 90, "default": 30})
    assert r["to_delete"] == 2  # access 100d + error 100d
    assert r["size_freed_mb"] == 700

def test_projection():
    r = storage_projection(50, 5, 30)
    assert r["max_projected_gb"] == 150
    assert r["pct_of_max"] == 33.3
