from app.services.app_marketplace_app_app_page_header import build_page_header

def test_full():
    r = build_page_header(title="App Settings", subtitle="Manage your app",
        breadcrumbs=[{"label": "Home", "path": "/"}, {"label": "Settings", "path": "/settings"}],
        actions=[{"label": "Save", "type": "primary"}, {"label": "Cancel", "type": "secondary"}])
    assert r["title"] == "App Settings"
    assert r["has_breadcrumbs"]
    assert r["has_actions"]
    assert len(r["actions"]) == 2

def test_minimal():
    r = build_page_header(title="Dashboard")
    assert not r["has_breadcrumbs"]
    assert not r["has_actions"]
    assert r["subtitle"] is None

def test_xss():
    r = build_page_header(title="<script>xss</script>")
    assert "<script>" not in r["title"]
