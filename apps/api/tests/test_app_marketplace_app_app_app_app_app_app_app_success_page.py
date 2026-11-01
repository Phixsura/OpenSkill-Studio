from app.services.app_marketplace_app_app_app_app_app_app_app_success_page import build_success_page

def test_installed():
    r = build_success_page(action="installed", app_name="Slack Bot")
    assert "Installed" in r["title"]
    assert "Slack Bot" in r["body"]
    assert r["show_confetti"]
    assert len(r["next"]) == 3

def test_deployed():
    r = build_success_page(action="deployed")
    assert "Deploy" in r["title"]
    assert not r["show_confetti"]
