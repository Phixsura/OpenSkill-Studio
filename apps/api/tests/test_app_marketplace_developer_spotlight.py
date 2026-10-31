from app.services.app_marketplace_developer_spotlight import select_spotlight_developers, build_spotlight_card

def test_select():
    devs = [{"display_name": "A", "published_apps": 1, "total_installs": 100, "avg_rating": 3, "verified": False},
            {"display_name": "B", "published_apps": 5, "total_installs": 5000, "avg_rating": 4.5, "verified": True},
            {"display_name": "C", "published_apps": 3, "total_installs": 2000, "avg_rating": 4.0, "verified": True}]
    r = select_spotlight_developers(developers=devs, limit=2)
    assert r[0]["display_name"] == "B"
    assert len(r) == 2

def test_card():
    c = build_spotlight_card(developer={"display_name": "DevCo", "slug": "devco", "bio": "We build tools", "verified": True,
                                          "published_apps": 5, "total_installs": 2000, "avg_rating": 4.5},
                               top_apps=[{"name": "App1", "slug": "app1"}, {"name": "App2", "slug": "app2"}])
    assert c["name"] == "DevCo"
    assert c["avatar_initial"] == "D"
    assert len(c["top_apps"]) == 2
    assert c["stats"]["apps"] == 5
