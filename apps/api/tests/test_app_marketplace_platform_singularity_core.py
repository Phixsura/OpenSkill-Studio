from app.services.app_marketplace_platform_singularity_core import get_singularity_core
def test_singularity_core():
    r = get_singularity_core()
    assert r["singularities"] > 4000
    assert r["black_hole"] is False
    assert r["white_hole"] is True
    assert "GREEN" in r["hawking_radiation"]
    assert "NEVER STOPS" in r["status"]
