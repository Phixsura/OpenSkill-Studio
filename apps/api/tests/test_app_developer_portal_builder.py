from app.services.app_developer_portal_builder import build_portal_page

def test_build():
    p = build_portal_page(
        developer={"display_name": "Dev", "verified": True},
        apps=[{"name": "App1", "status": "published"}],
        completed_steps={"create_account", "create_app"},
        total_installs=100,
    )
    assert p["developer"]["name"] == "Dev"
    assert len(p["quick_actions"]) >= 3
    assert p["portal_version"] == "1.0"
    assert "config" in p

def test_new_developer():
    p = build_portal_page(developer={"display_name": "New"}, apps=[], completed_steps=set())
    assert p["is_new"] is True

def test_quick_actions():
    p = build_portal_page(developer={"display_name": "X"}, apps=[], completed_steps=set())
    labels = [a["label"] for a in p["quick_actions"]]
    assert "Create App" in labels
    assert "Documentation" in labels
