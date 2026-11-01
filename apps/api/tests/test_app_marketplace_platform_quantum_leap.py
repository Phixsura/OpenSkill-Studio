from app.services.app_marketplace_platform_quantum_leap import get_quantum_leap
def test_quantum_leap():
    r = get_quantum_leap()
    assert r["leaps"] == r["landings_perfect"]
    assert r["landings_failed"] == 0
    assert r["transition_time"].startswith("ZERO")
    assert "INFINITE" in r["coherence_time"]
    assert "NEVER STOPS" in r["status"]
