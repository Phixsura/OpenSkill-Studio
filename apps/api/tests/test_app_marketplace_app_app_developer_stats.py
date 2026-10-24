from app.services.app_marketplace_app_app_developer_stats import build_developer_stats

def test_stats():
    dev = {"name": "Alice", "member_since": "2024-01-01"}
    apps = [
        {"name": "SuperApp", "installs": 80000, "review_count": 200, "rating": 4.8},
        {"name": "MiniApp", "installs": 25000, "review_count": 50, "rating": 4.2},
    ]
    r = build_developer_stats(developer=dev, apps=apps)
    assert r["developer"] == "Alice"
    assert r["summary"]["total_installs"] == 105000
    assert r["summary"]["total_apps"] == 2
    assert r["summary"]["top_app"] == "SuperApp"
    assert any(b["id"] == "100k_installs" for b in r["badges"])
    assert any(b["id"] == "top_quality" for b in r["badges"])

def test_empty():
    r = build_developer_stats(developer={"name": "Bob"}, apps=[])
    assert r["summary"]["total_apps"] == 0
    assert len(r["badges"]) == 0
