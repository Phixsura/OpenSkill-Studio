from app.services.app_marketplace_app_app_app_app_app_publish_page import build_publish_page

def test_ready():
    checks = {s: True for s in ["manifest", "tests", "security", "screenshots",
                                  "description", "privacy", "changelog", "review"]}
    r = build_publish_page(app={"name": "SuperApp"}, check_results=checks,
                            version="2.0.0", release_notes="Big update")
    assert r["can_publish"]
    assert r["score"] == 100
    assert "Publish" in r["cta"]

def test_not_ready():
    r = build_publish_page(app={"name": "X"}, check_results={"manifest": True}, version="1.0")
    assert not r["can_publish"]
    assert r["passed"] == 1
    assert "7 remaining" in r["cta"]
