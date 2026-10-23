from app.services.app_marketplace_app_app_app_app_app_app_app_cdn_optimizer import analyze_cdn, suggest_optimizations

def test_analyze():
    assets = [
        {"path": "/app.js", "type": "script", "size_kb": 200, "cached": True},
        {"path": "/style.css", "type": "style", "size_kb": 50, "cached": True},
        {"path": "/logo.png", "type": "image", "size_kb": 800, "cached": False},
    ]
    r = analyze_cdn(assets)
    assert r["cached"] == 2
    assert r["hit_ratio"] == 66.7
    assert r["by_type"]["image"] == 1

def test_suggestions():
    assets = [
        {"path": "/big.js", "type": "script", "size_kb": 500, "cached": False},
        {"path": "/hero.png", "type": "image", "size_kb": 1200, "cached": True},
    ]
    s = suggest_optimizations(assets)
    assert len(s) == 2  # uncached large + large image
