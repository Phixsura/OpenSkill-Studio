from app.services.app_marketplace_app_app_app_app_app_app_app_traffic_mirror import (
    create_mirror, process_mirror, mirror_summary,
)

def test_mirror():
    m = create_mirror("prod-api", "shadow-api", sample_rate=0.5)
    r = process_mirror(m, 100, 2)
    assert r["mirrored"] == 50
    assert m["mirrored"] == 50

def test_summary():
    mirrors = [
        create_mirror("a", "b"), create_mirror("c", "d", sample_rate=0.1),
    ]
    mirrors[0]["mirrored"] = 1000
    mirrors[1]["mirrored"] = 100
    r = mirror_summary(mirrors)
    assert r["total_mirrored"] == 1100
    assert r["active"] == 2
