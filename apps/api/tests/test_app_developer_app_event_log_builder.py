from app.services.app_developer_app_event_log_builder import build_event_log_page

def test_page():
    p = build_event_log_page(events=[{"id": "e1"}], total=100, page=1, per_page=20)
    assert p["total_pages"] == 5
