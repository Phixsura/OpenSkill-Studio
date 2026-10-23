from app.services.app_marketplace_app_ping import ping
def test_ping():
    assert ping()["pong"] is True
