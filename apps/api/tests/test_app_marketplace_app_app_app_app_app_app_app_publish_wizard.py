from app.services.app_marketplace_app_app_app_app_app_app_app_publish_wizard import build_publish_wizard

def test_wizard():
    r = build_publish_wizard(["listing", "security"])
    assert r["completed"] == 2
    assert r["current_step"] == "testing"
    assert r["progress_pct"] == 40
    assert not r["ready_to_submit"]

def test_ready():
    r = build_publish_wizard(["listing", "security", "testing", "legal"])
    assert r["ready_to_submit"]
    assert r["current_step"] == "submit"
