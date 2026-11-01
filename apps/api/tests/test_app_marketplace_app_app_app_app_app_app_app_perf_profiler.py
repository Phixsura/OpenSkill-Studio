from app.services.app_marketplace_app_app_app_app_app_app_app_perf_profiler import profile_request, compare_profiles

def test_profile():
    r = profile_request([
        {"name": "handler", "duration_ms": 200, "parent": None},
        {"name": "db_query", "duration_ms": 150, "parent": "handler"},
        {"name": "serialize", "duration_ms": 30, "parent": "handler"},
    ])
    assert r["total_ms"] == 380
    assert r["bottleneck"] == "handler"
    # handler self_time = 200 - 150 - 30 = 20
    handler_st = next(s for s in r["self_times"] if s["name"] == "handler")
    assert handler_st["self_ms"] == 20

def test_compare():
    before = {"total_ms": 500}
    after = {"total_ms": 350}
    r = compare_profiles(before, after)
    assert r["improved"]
    assert r["improvement_pct"] == 30.0
