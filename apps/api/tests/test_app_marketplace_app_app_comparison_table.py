from app.services.app_marketplace_app_app_comparison_table import build_comparison_table

def test_compare():
    apps = [
        {"id": "a1", "name": "App A", "rating": 4.5, "installs": 5000, "has_api": True},
        {"id": "a2", "name": "App B", "rating": 4.8, "installs": 3000, "has_api": False},
    ]
    r = build_comparison_table(apps=apps, criteria=["rating", "installs", "has_api"])
    assert len(r["rows"]) == 3
    assert r["winner"] == "a1"  # higher total score
    assert len(r["apps"]) == 2

def test_too_few():
    r = build_comparison_table(apps=[{"id": "a1"}], criteria=[])
    assert "error" in r
