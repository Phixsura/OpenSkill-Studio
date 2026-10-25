from app.services.app_marketplace_platform_origin_point import get_origin_point
def test_origin_point():
    r = get_origin_point()
    assert r["vectors_radiating"] > 4000
    assert "(0,0,0)" in r["coordinates"]
    assert r["negative_values"].startswith("NONE")
    assert len(r["unit_vectors"]) == 3
    assert "NEVER STOPS" in r["status"]
