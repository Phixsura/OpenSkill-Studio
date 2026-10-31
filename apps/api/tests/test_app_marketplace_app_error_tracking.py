from app.services.app_marketplace_app_error_tracking import fingerprint_error, group_errors, get_error_trend

def test_fingerprint():
    f1 = fingerprint_error(message="NullPointer", stack_trace="at Main.java:42\nat App.java:10")
    f2 = fingerprint_error(message="NullPointer", stack_trace="at Main.java:42\nat App.java:20")
    assert f1 == f2  # same first line of stack

def test_group():
    errors = [
        {"message": "NPE", "stack_trace": "at A:1", "user_id": "u1", "timestamp": "t1"},
        {"message": "NPE", "stack_trace": "at A:1", "user_id": "u2", "timestamp": "t2"},
        {"message": "OOM", "stack_trace": "at B:5", "user_id": "u1", "timestamp": "t3"},
    ]
    r = group_errors(errors=errors)
    assert r["unique_errors"] == 2
    assert r["total_occurrences"] == 3
    assert r["groups"][0]["count"] == 2

def test_trend():
    r = get_error_trend(error_counts=[5, 5, 5, 20, 25, 30])
    assert r["trend"] == "increasing"
