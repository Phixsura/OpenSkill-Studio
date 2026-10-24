from app.services.app_marketplace_featured_v2 import compute_trending_score, select_featured_apps, build_featured_section

def test_score():
    s = compute_trending_score(app={"recent_installs": 100, "recent_reviews": 10, "avg_rating": 4.5})
    assert s > 0

def test_select():
    apps = [{"id": "a1", "recent_installs": 50, "avg_rating": 4.0},
            {"id": "a2", "recent_installs": 200, "avg_rating": 4.5},
            {"id": "a3", "recent_installs": 10, "avg_rating": 3.0}]
    r = select_featured_apps(apps=apps, editorial_picks=["a3"], max_featured=3)
    assert r["editorial_count"] == 1
    assert r["count"] == 3
    assert r["featured"][0]["id"] == "a3"  # editorial pick first

def test_section():
    featured = [{"id": f"a{i}"} for i in range(8)]
    s = build_featured_section(featured=featured)
    assert s["hero"]["id"] == "a0"
    assert len(s["grid"]) == 4
    assert len(s["rest"]) == 3
