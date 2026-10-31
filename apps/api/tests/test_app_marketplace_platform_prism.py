from app.services.app_marketplace_platform_prism import get_prism
def test_prism():
    r = get_prism()
    assert len(r["output_spectrum"]) == 7
    assert r["refraction_index"] > 4000
    assert r["total_internal_reflection"] is False
    assert "COMPLETE" in r["dispersion"]
    assert "NEVER STOPS" in r["status"]
