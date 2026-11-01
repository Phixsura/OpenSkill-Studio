from app.services.app_marketplace_app_app_app_app_app_app_app_newsletter import build_newsletter

def test_newsletter():
    r = build_newsletter(subject="OpenSkill Weekly #42", sections=[
        {"type": "hero", "title": "New: SSO Support", "body": "Enterprise authentication is here", "cta": "Learn More"},
        {"type": "text", "title": "Platform Updates", "body": "We shipped 15 new features this week"},
        {"type": "apps", "title": "Trending Apps", "body": "Check out the hottest new integrations"},
    ])
    assert r["subject"] == "OpenSkill Weekly #42"
    assert r["section_count"] == 3
    assert r["word_count"] > 0
    assert r["read_time_min"] >= 1
