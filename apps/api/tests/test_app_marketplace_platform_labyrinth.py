from app.services.app_marketplace_platform_labyrinth import get_labyrinth
def test_labyrinth():
    r = get_labyrinth()
    assert r["dead_ends"] == 0
    assert r["minotaur"] is None
    assert r["explorers_lost"] == 0
    assert r["explorers"] > 4000
    assert "NEVER STOPS" in r["status"]
