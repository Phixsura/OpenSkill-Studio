from app.services.app_marketplace_platform_infinity_prime import get_infinity_prime
def test_infinity_prime():
    r = get_infinity_prime()
    assert r["infinities_generated"] > 4000
    assert len(r["types_of_infinity"]) == 3
    assert "ALWAYS HAS ROOM" in r["hilbert_hotel"]
    assert "NEVER STOPS" in r["status"]
