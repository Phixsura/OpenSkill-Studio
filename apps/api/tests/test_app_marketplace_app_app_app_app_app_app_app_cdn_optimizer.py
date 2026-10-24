from app.services.app_marketplace_app_app_app_app_app_app_app_cdn_optimizer import analyze_cdn

def test_analyze():
    r = analyze_cdn([
        {"cache": "hit", "region": "us-east"},
        {"cache": "hit", "region": "us-east"},
        {"cache": "miss", "region": "eu-west"},
        {"cache": "hit", "region": "eu-west"},
    ])
    assert r["hit_rate"] == 75.0
    assert r["hits"] == 3
    assert r["bandwidth_saved_mb"] == 1.5
    assert len(r["regions"]) == 2
