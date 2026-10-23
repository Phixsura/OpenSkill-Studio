from app.services.app_marketplace_app_developer_newsletter import create_newsletter, get_newsletter_stats

def test_create():
    sections = [
        {"heading": "What's New", "body": "We launched dark mode!", "cta_label": "Try it", "cta_url": "/settings"},
        {"heading": "Tips", "body": "Optimize your API calls."},
    ]
    r = create_newsletter(title="Dev Update #42", sections=sections, edition=42)
    assert r["newsletter_id"].startswith("nl_")
    assert r["edition"] == 42
    assert r["section_count"] == 2
    assert r["status"] == "draft"

def test_xss():
    r = create_newsletter(title="<script>xss</script>", sections=[{"heading": "<b>bold</b>"}], edition=1)
    assert "<script>" not in r["title"]

def test_stats():
    newsletters = [{"sent_count": 1000, "opened_count": 400},
                   {"sent_count": 1000, "opened_count": 350}]
    r = get_newsletter_stats(newsletters=newsletters)
    assert r["avg_open_rate"] == 37.5
