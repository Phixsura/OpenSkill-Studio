from app.services.app_marketplace_comparison_result import build_comparison_result

def test_result():
    apps = [{"id": "a1", "name": "App A", "rating": 4.5, "installs": 500},
            {"id": "a2", "name": "App B", "rating": 4.0, "installs": 2000}]
    r = build_comparison_result(apps=apps, dimensions=["rating", "installs"])
    assert r["winner"]["id"] == "a2"  # higher total
    assert len(r["apps"]) == 2
    assert "a1,a2" in r["shareable_url"]

def test_too_few():
    r = build_comparison_result(apps=[{"id": "a1"}], dimensions=[])
    assert r.get("error")
