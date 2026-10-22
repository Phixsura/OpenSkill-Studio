from app.services.app_developer_dashboard_builder import build_developer_dashboard

def test_build():
    d = build_developer_dashboard(
        developer={"display_name": "Dev Co", "verified": True},
        apps=[{"name": "App1", "status": "published"}],
        completed_steps={"create_account", "create_app"},
        total_installs=100,
    )
    assert d["developer"]["name"] == "Dev Co"
    assert d["stats"]["app_count"] == 1
    assert d["onboarding"]["completed_steps"] == 2

def test_new_developer():
    d = build_developer_dashboard(developer={"display_name": "New"}, apps=[], completed_steps=set())
    assert d["is_new"] is True

def test_experienced():
    d = build_developer_dashboard(developer={"display_name": "Pro"}, apps=[{} for _ in range(5)],
        completed_steps={"create_account", "create_app", "add_manifest", "create_version", "submit_review"})
    assert d["is_new"] is False
