from app.services.app_marketplace_app_app_app_app_app_app_app_dep_matrix import build_matrix, find_hubs

def test_matrix():
    r = build_matrix(["api", "web", "db", "cache"],
                       {"api": ["db", "cache"], "web": ["api"], "db": [], "cache": []})
    assert r["total_deps"] == 3
    assert r["matrix"]["api"]["db"] is True
    assert r["matrix"]["db"]["api"] is False

def test_hubs():
    m = build_matrix(["api", "web", "worker", "db"],
                       {"api": ["db"], "web": ["api", "db"], "worker": ["db"], "db": []})
    r = find_hubs(m)
    assert r["most_depended_on"] == "db"
    assert r["incoming"] == 3
