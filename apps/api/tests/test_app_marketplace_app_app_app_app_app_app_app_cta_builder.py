from app.services.app_marketplace_app_app_app_app_app_app_app_cta_builder import get_cta, get_next_cta

def test_cta():
    r = get_cta("upgrade")
    assert r["button"] == "View Plans"
    assert r["icon"] == "⬆️"

def test_next():
    assert get_next_cta(has_app=False, has_key=False, has_team=False, plan="free")["button"] == "Create App"
    assert get_next_cta(has_app=True, has_key=False, has_team=False, plan="free")["button"] == "Generate Key"
    assert get_next_cta(has_app=True, has_key=True, has_team=False, plan="free")["button"] == "View Plans"
    assert get_next_cta(has_app=True, has_key=True, has_team=False, plan="pro")["button"] == "Invite"
