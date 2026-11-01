from app.services.app_marketplace_400k_crossed_official_final import the_400k_line
def test_400k_crossed():
    assert the_400k_line()["crossed"]
