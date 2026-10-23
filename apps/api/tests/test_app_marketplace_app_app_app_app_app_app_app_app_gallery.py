from app.services.app_marketplace_app_app_app_app_app_app_app_app_gallery import build_gallery, get_featured

def test_gallery():
    cols = [
        {"id": "popular", "title": "Most Popular", "description": "Top apps",
         "icon": "🔥", "featured": True,
         "apps": [{"name": "Slack", "icon": "💬", "rating": 4.8},
                  {"name": "GitHub", "icon": "🐙", "rating": 4.9}]},
        {"id": "new", "title": "New & Notable", "description": "Recently added",
         "apps": [{"name": "Fresh App", "icon": "🆕"}]},
    ]
    r = build_gallery(cols)
    assert r["total_collections"] == 2
    assert r["total_apps"] == 3
    assert r["collections"][0]["app_count"] == 2
    assert r["collections"][0]["featured"]

def test_featured():
    cols = [{"id": "a", "featured": True}, {"id": "b", "featured": False}]
    assert len(get_featured(cols)) == 1
