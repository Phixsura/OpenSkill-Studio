from app.services.app_marketplace_app_app_app_app_app_app_app_rollback_tracker import RollbackTracker

def test_track():
    rt = RollbackTracker()
    rt.record("api", "2.0", "1.9", "high_error_rate", "automated")
    rt.record("api", "2.1", "2.0", "latency_spike", "manual")
    rt.record("web", "3.0", "2.9", "high_error_rate")
    by_reason = rt.by_reason()
    assert by_reason["high_error_rate"] == 2
    by_svc = rt.by_service()
    assert by_svc["api"] == 2
    s = rt.stats()
    assert s["automated"] == 2
    assert s["manual"] == 1
