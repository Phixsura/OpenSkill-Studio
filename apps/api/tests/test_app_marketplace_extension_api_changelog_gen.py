from app.services.app_marketplace_extension_api_changelog_gen import ApiChangelogGenService

def test_diff():
    svc = ApiChangelogGenService()
    old = [{"path": "/users", "method": "GET"}, {"path": "/old", "method": "DELETE"}]
    new = [{"path": "/users", "method": "GET"}, {"path": "/new", "method": "POST"}]
    cl = svc.diff(old, new, "1.0", "2.0")
    assert cl.has_breaking is True
    assert cl.summary["added"] == 1
    assert cl.summary["removed"] == 1

def test_format():
    svc = ApiChangelogGenService()
    old = [{"path": "/a", "method": "GET"}]
    new = [{"path": "/a", "method": "GET"}, {"path": "/b", "method": "POST"}]
    cl = svc.diff(old, new, "1.0", "1.1")
    md = svc.format_markdown(cl)
    assert "POST /b" in md
    assert "Added" in md

def test_no_changes():
    svc = ApiChangelogGenService()
    eps = [{"path": "/a", "method": "GET"}]
    cl = svc.diff(eps, eps, "1.0", "1.0")
    assert len(cl.changes) == 0
