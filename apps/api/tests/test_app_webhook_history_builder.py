from app.services.app_webhook_history_builder import build_webhook_history_page

def test_page():
    p = build_webhook_history_page(deliveries=[{"id": "d1"}], total=50, page=1, per_page=20, success_rate=99.0)
    assert p["total_pages"] == 3
    assert p["success_rate"] == 99.0
