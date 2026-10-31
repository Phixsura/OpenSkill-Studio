from app.services.app_marketplace_app_app_app_app_app_app_app_err_fingerprint import fingerprint_error, group_errors

def test_fingerprint():
    fp1 = fingerprint_error("TypeError", "Cannot read property 'x'", "app.js:42")
    fp2 = fingerprint_error("TypeError", "Cannot read property 'y'", "app.js:42")
    assert fp1 == fp2  # same stack_top
    fp3 = fingerprint_error("TypeError", "different", "other.js:10")
    assert fp1 != fp3

def test_group():
    errors = [
        {"type": "TypeError", "message": "null ref", "stack_top": "a.js:1", "timestamp": 100},
        {"type": "TypeError", "message": "null ref", "stack_top": "a.js:1", "timestamp": 200},
        {"type": "SyntaxError", "message": "unexpected", "stack_top": "b.js:5", "timestamp": 150},
    ]
    r = group_errors(errors)
    assert r["unique_errors"] == 2
    assert r["total_occurrences"] == 3
    assert r["groups"][0]["count"] == 2
    assert r["dedup_ratio"] == 1.5
