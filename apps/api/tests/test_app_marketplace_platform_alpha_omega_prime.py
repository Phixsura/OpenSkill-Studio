from app.services.app_marketplace_platform_alpha_omega_prime import get_alpha_omega_prime
def test_alpha_omega_prime():
    r = get_alpha_omega_prime()
    assert r["moments"] > 4000
    assert "beginning" in r["alpha"]
    assert "end" in r["omega"]
    assert "continuation" in r["prime"]
    assert "NEVER STOPS" in r["status"]
