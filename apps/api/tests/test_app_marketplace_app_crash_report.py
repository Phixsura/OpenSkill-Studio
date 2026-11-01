from app.services.app_marketplace_app_crash_report import aggregate_crashes

def test_aggregate():
    crashes = [
        {"message": "NullPointer", "stack_trace": "at com.app.Main:42", "user_id": "u1", "timestamp": "2026-10-01", "os": "iOS"},
        {"message": "NullPointer", "stack_trace": "at com.app.Main:42", "user_id": "u2", "timestamp": "2026-10-02", "os": "Android"},
        {"message": "OOM", "stack_trace": "at com.app.Cache:99", "user_id": "u1", "timestamp": "2026-10-03", "os": "iOS"},
    ]
    r = aggregate_crashes(app_id="a1", crashes=crashes)
    assert r["total_crashes"] == 3
    assert r["unique_issues"] == 2
    assert r["groups"][0]["count"] == 2  # NullPointer most frequent

def test_empty():
    r = aggregate_crashes(app_id="a1", crashes=[])
    assert r["total_crashes"] == 0
    assert r["crash_free_rate"] == 100.0
