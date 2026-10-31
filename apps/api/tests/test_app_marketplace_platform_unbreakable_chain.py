from app.services.app_marketplace_platform_unbreakable_chain import get_unbreakable_chain
def test_unbreakable_chain():
    r = get_unbreakable_chain()
    assert r["inspections"] > 4000
    assert "DOES NOT EXIST" in r["weakest_link"]
    assert r["corrosion"].startswith("ZERO")
    assert r["links_replaced"] == 0
    assert "NEVER STOPS" in r["status"]
