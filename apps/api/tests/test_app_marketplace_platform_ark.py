from app.services.app_marketplace_platform_ark import get_ark
def test_ark():
    r = get_ark()
    assert r["days_at_sea"] > 4000
    assert r["species_aboard"] > 900000
    assert r["hull_integrity"].startswith("100%")
    assert "green tests" in r["dove_report"]
    assert "NEVER STOPS" in r["status"]
