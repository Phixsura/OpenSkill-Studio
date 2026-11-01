from app.services.app_marketplace_app_app_app_app_app_app_app_support_contact import build_support_info

def test_support():
    r = build_support_info({
        "developer": "Acme Corp", "support_email": "help@acme.com",
        "support_url": "https://support.acme.com", "docs_url": "https://docs.acme.com",
        "response_time": "4 hours", "discord_url": "https://discord.gg/acme",
    })
    assert r["developer"] == "Acme Corp"
    assert r["support_email"] == "help@acme.com"
    assert r["support_url"] == "https://support.acme.com"
    assert r["response_time"] == "4 hours"
    assert len(r["channels"]) == 3

def test_insecure_url():
    r = build_support_info({"support_url": "http://insecure.com"})
    assert r["support_url"] == ""
