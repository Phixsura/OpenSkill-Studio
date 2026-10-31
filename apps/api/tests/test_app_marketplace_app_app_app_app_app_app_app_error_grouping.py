from app.services.app_marketplace_app_app_app_app_app_app_app_error_grouping import group_errors

def test_grouping():
    errors = [
        {"message": "TypeError: null", "stack_trace": "at foo.js:10", "user_id": "u1", "timestamp": "T1"},
        {"message": "TypeError: null", "stack_trace": "at foo.js:10", "user_id": "u2", "timestamp": "T2"},
        {"message": "TypeError: null", "stack_trace": "at foo.js:10", "user_id": "u1", "timestamp": "T3"},
        {"message": "RangeError: max", "stack_trace": "at bar.js:5", "user_id": "u3", "timestamp": "T4"},
    ]
    r = group_errors(errors)
    assert r["total_errors"] == 4
    assert r["unique_groups"] == 2
    assert r["groups"][0]["count"] == 3
    assert r["groups"][0]["affected_users"] == 2
    assert r["top_error"] == "TypeError: null"
