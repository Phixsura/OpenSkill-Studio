from app.services.app_marketplace_app_app_app_app_app_app_app_app_sharing import build_share_preview

def test_share():
    r = build_share_preview({"id": "slack-bot", "name": "Slack Bot", "description": "Best integration"})
    assert "Slack Bot" in r["title"]
    assert "marketplace.openskill.io" in r["url"]
    assert "twitter.com" in r["share_links"]["twitter"]
    assert r["share_links"]["copy"] == r["url"]
