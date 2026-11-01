from app.services.app_marketplace_platform_lodestone import get_lodestone
def test_lodestone():
    r = get_lodestone()
    assert r["alignments"] > 4000
    assert r["demagnetization"] == "IMPOSSIBLE — permanent magnet"
    assert len(r["attracted_particles"]) == 4
    assert "NEVER STOPS" in r["status"]
