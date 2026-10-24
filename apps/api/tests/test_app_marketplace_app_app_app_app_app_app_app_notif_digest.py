from app.services.app_marketplace_app_app_app_app_app_app_app_notif_digest import build_digest

def test_digest():
    notifs = [
        {"title": "Deploy succeeded", "body": "v2.1 deployed", "category": "deploys", "priority": "normal"},
        {"title": "Error spike", "body": "500 errors up 200%", "category": "alerts", "priority": "high"},
        {"title": "New review", "body": "Bob reviewed PR #42", "category": "reviews", "priority": "normal"},
        {"title": "Disk warning", "body": "90% full", "category": "alerts", "priority": "high"},
    ]
    r = build_digest(notifs)
    assert r["total"] == 4
    assert r["high_priority"] == 2
    assert r["categories"] == 3
    assert len(r["sections"]) == 3
