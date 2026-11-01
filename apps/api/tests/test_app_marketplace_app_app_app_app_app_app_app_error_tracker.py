from app.services.app_marketplace_app_app_app_app_app_app_app_error_tracker import ErrorTracker

def test_track():
    et = ErrorTracker()
    et.track("TypeError", "Cannot read property", service="api")
    et.track("TypeError", "Cannot read property", service="api")
    et.track("ValueError", "Invalid input", service="worker")
    top = et.top_errors()
    assert top[0]["count"] == 2
    assert et.stats()["unique_groups"] == 2
