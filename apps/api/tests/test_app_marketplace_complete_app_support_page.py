from app.services.app_marketplace_complete_app_support_page import build_complete_support_page

def test_page():
    p = build_complete_support_page(
        app={"id": "a1", "name": "App"},
        faq=[{"q": "How?"}], open_tickets=[{"priority": "normal"}, {"priority": "urgent"}],
        docs_url="/docs", support_email="help@app.com", community_url="/community",
        developer={"display_name": "DevCo", "avg_response_hours": 12})
    assert p["tabs"][1]["urgent"] == 1
    assert p["developer"]["response_time"] == 12
    assert p["contact"]["has_email"]
