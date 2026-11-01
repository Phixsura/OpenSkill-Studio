from app.services.app_marketplace_app_app_clipboard_share import build_share_options

def test_share():
    r = build_share_options(app_name="MyApp", app_url="https://example.com/app", description="Great app")
    assert r["direct_link"] == "https://example.com/app"
    assert "[MyApp]" in r["markdown"]
    assert "twitter.com" in r["twitter"]
    assert "iframe" in r["embed_iframe"]

def test_invalid_scheme():
    r = build_share_options(app_name="X", app_url="javascript:alert(1)")
    assert "error" in r

def test_xss():
    r = build_share_options(app_name="<script>", app_url="https://example.com")
    assert "<script>" not in r["html_link"]
