from app.services.app_marketplace_app_startup import startup_check
def test_startup():
    r = startup_check()
    assert r["started"]
    assert r["modules_loaded"] == 10
