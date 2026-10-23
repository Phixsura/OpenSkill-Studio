from app.services.app_marketplace_app_app_app_app_app_app_app_org_switcher import build_org_list, get_org_context

def test_org_list():
    r = build_org_list([
        {"id": "org1", "name": "Acme", "role": "admin", "plan": "pro"},
        {"id": "org2", "name": "Side Project", "role": "member", "plan": "free"},
    ], current_org_id="org1")
    assert r["total"] == 2
    assert r["current"]["name"] == "Acme"
    assert r["current"]["active"]
    assert r["can_create"]

def test_context():
    r = get_org_context({"id": "org1", "name": "Acme", "plan": "pro"})
    assert "sso" in r["features"]
    assert len(r["features"]) == 3
