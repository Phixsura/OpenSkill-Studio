from app.services.app_marketplace_app_app_webhook_filter import match_event, build_filter_summary

def test_exact():
    r = match_event(event_type="app.installed", filters=[{"pattern": "app.installed", "mode": "exact"}])
    assert r["matched"]

def test_prefix():
    r = match_event(event_type="app.updated", filters=[{"pattern": "app.", "mode": "prefix"}])
    assert r["matched"]

def test_regex():
    r = match_event(event_type="deploy.v2.completed", filters=[{"pattern": r"deploy\.v\d+\..*", "mode": "regex"}])
    assert r["matched"]

def test_no_match():
    r = match_event(event_type="user.login", filters=[{"pattern": "app.installed", "mode": "exact"}])
    assert not r["matched"]

def test_summary_with_test():
    filters = [{"pattern": "app.", "mode": "prefix"}]
    r = build_filter_summary(filters=filters, test_events=["app.installed", "user.login"])
    assert r["test_results"][0]["matched"]
    assert not r["test_results"][1]["matched"]
