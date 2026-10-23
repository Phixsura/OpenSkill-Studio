from app.services.app_marketplace_app_shutdown import graceful_shutdown
def test_shutdown():
    r = graceful_shutdown()
    assert r["shutdown"]
    assert r["cleanup_complete"]
