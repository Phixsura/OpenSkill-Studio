from app.services.app_marketplace_app_app_app_app_app_app_app_review_queue import build_review_queue

def test_queue():
    r = build_review_queue([
        {"app_name": "App A", "developer": "Dev 1", "stage": "submitted"},
        {"app_name": "App B", "developer": "Dev 2", "stage": "manual_review"},
        {"app_name": "App C", "developer": "Dev 3", "stage": "approved"},
        {"app_name": "App D", "developer": "Dev 4", "stage": "rejected"},
    ])
    assert r["total"] == 4
    assert r["pending_count"] == 2
    assert r["approved_count"] == 1
    assert r["rejected_count"] == 1
