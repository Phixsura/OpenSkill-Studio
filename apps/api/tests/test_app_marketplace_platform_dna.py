from app.services.app_marketplace_platform_dna import get_platform_dna
def test_dna():
    r = get_platform_dna()
    assert len(r["strands"]) == 6
    assert r["mutations"] == "NONE — all genes stable and optimal"
    assert "NEVER STOPS" in r["status"]
