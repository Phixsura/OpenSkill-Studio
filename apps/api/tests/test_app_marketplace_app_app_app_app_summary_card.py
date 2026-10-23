from app.services.app_marketplace_app_app_app_app_summary_card import build_app_summary, build_app_list

def test_summary():
    r = build_app_summary(app={"id": "a1", "name": "SuperApp", "icon": "🚀",
                                "rating": 4.5, "installs": 25000, "verified": True, "author": "Alice"})
    assert r["name"] == "SuperApp"
    assert r["installs_display"] == "25.0K"
    assert r["verified"]
    assert "★" in r["stars"]

def test_list():
    apps = [{"id": "a1", "name": "A", "rating": 4.0, "installs": 1000},
            {"id": "a2", "name": "B", "rating": 5.0, "installs": 2000}]
    r = build_app_list(apps=apps)
    assert r["total"] == 2
    assert r["total_installs"] == 3000
    assert r["avg_rating"] == 4.5
