from app.services.app_marketplace_app_app_app_app_app_app_app_log_level_ctrl import LogLevelController

def test_default():
    lc = LogLevelController("info")
    assert lc.get_level("api") == "info"
    assert lc.should_log("api", "error")
    assert not lc.should_log("api", "debug")

def test_override():
    lc = LogLevelController("info")
    lc.set_level("api", "debug")
    assert lc.get_level("api") == "debug"
    assert lc.should_log("api", "debug")

def test_reset():
    lc = LogLevelController("warn")
    lc.set_level("api", "debug")
    lc.reset("api")
    assert lc.get_level("api") == "warn"
    assert lc.status()["services_overridden"] == 0
