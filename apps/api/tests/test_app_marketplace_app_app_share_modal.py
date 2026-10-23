from app.services.app_marketplace_app_app_share_modal import build_share_options

def test_share():
    r = build_share_options(app_name="Auth SDK", app_url="https://marketplace.dev/apps/auth",
        description="Best authentication solution for developers")
    assert r["app_name"] == "Auth SDK"
    assert len(r["platforms"]) == 3
    assert "twitter.com" in r["platforms"][0]["url"]
    assert "linkedin.com" in r["platforms"][1]["url"]
    assert r["platforms"][2]["url"].startswith("mailto:")

def test_xss():
    r = build_share_options(app_name="<script>xss</script>", app_url="https://x.com", description="ok")
    assert "<script>" not in r["app_name"]
    assert "<script>" not in r["embed_code"]
