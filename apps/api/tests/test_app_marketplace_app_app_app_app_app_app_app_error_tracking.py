from app.services.app_marketplace_app_app_app_app_app_app_app_error_tracking import track_errors

def test_tracking():
    errors = [
        {"type": "TypeError", "message": "undefined is not a function", "user_id": "u1", "timestamp": "2026-10-24T10:00"},
        {"type": "TypeError", "message": "undefined is not a function", "user_id": "u2", "timestamp": "2026-10-24T10:05"},
        {"type": "NetworkError", "message": "Failed to fetch", "user_id": "u1", "timestamp": "2026-10-24T10:10"},
    ]
    r = track_errors(errors=errors)
    assert r["total_errors"] == 3
    assert r["unique_errors"] == 2
    assert r["groups"][0]["count"] == 2
    assert r["groups"][0]["affected_users"] == 2

def test_empty():
    r = track_errors(errors=[])
    assert r["total_errors"] == 0
