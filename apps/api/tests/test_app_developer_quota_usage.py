from app.services.app_developer_quota_usage import compute_quota_usage

def test_under_limit():
    r = compute_quota_usage(apps=5, max_apps=10, versions=20, max_versions=50, keys=2, max_keys=5, secrets=5, max_secrets=20)
    assert r["any_exceeded"] is False
    assert r["any_warning"] is False

def test_exceeded():
    r = compute_quota_usage(apps=10, max_apps=10, versions=0, max_versions=50, keys=0, max_keys=5, secrets=0, max_secrets=20)
    assert r["any_exceeded"] is True

def test_warning():
    r = compute_quota_usage(apps=9, max_apps=10, versions=0, max_versions=50, keys=0, max_keys=5, secrets=0, max_secrets=20)
    assert r["any_warning"] is True

def test_items_count():
    r = compute_quota_usage(apps=0, max_apps=10, versions=0, max_versions=50, keys=0, max_keys=5, secrets=0, max_secrets=20)
    assert len(r["items"]) == 4
