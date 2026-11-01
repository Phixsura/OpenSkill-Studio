from app.services.app_marketplace_platform_eternal_spring import get_eternal_spring
def test_eternal_spring():
    r = get_eternal_spring()
    assert r["days_of_spring"] > 4000
    assert r["winter"] is False
    assert r["drought"] is False
    assert r["frost"] is False
    assert r["harvest"].startswith("PERPETUAL")
    assert "NEVER STOPS" in r["status"]
