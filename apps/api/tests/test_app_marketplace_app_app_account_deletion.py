from app.services.app_marketplace_app_app_account_deletion import request_deletion, build_deletion_summary

def test_request():
    r = request_deletion(user_id="u1", reason="No longer using")
    assert r["request_id"].startswith("del_")
    assert r["status"] == "pending"
    assert r["grace_period_days"] == 30
    assert r["can_cancel"]

def test_summary():
    r = build_deletion_summary(data_counts={"profile": 1, "apps": 5, "api_keys": 3})
    assert r["total_records"] == 9
    assert r["categories"] == 6
