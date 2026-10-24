from app.services.app_marketplace_app_app_app_app_app_app_app_dev_blog import build_blog_listing, get_related_posts

def test_listing():
    r = build_blog_listing([
        {"slug": "sso-launch", "title": "SSO is here!", "excerpt": "Enterprise auth", "author": "Team", "date": "2026-10-24", "tags": ["sso"], "featured": True},
        {"slug": "v3-release", "title": "v3 Released", "excerpt": "Major update", "author": "Team", "date": "2026-10-20"},
    ])
    assert r["total"] == 2
    assert len(r["featured"]) == 1

def test_related():
    posts = [
        {"slug": "a", "title": "A", "date": "1", "tags": ["sso", "auth"]},
        {"slug": "b", "title": "B", "date": "2", "tags": ["webhooks"]},
        {"slug": "c", "title": "C", "date": "3", "tags": ["auth", "security"]},
    ]
    r = get_related_posts(["auth"], posts)
    assert len(r) == 2
    assert r[0]["slug"] in ("a", "c")
