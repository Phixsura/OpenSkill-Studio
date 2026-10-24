from app.services.app_marketplace_app_app_version_badge import build_version_badge

def test_stable():
    r = build_version_badge(version="2.1.0", channel="stable")
    assert r["display"] == "v2.1.0"
    assert r["channel_info"]["icon"] == "✅"
    assert r["is_latest"]

def test_beta():
    r = build_version_badge(version="3.0.0-beta.1", channel="beta", is_latest=False)
    assert r["channel_info"]["label"] == "Beta"
    assert not r["is_latest"]
    assert "Beta" in r["full_label"]
