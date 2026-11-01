from app.services.app_marketplace_app_app_app_app_app_app_app_hot_reload import HotReloadManager

def test_reload():
    hrm = HotReloadManager()
    hrm.register("app", {"port": 8080, "debug": False})
    r1 = hrm.check_update("app", {"port": 8080, "debug": False})
    assert not r1["changed"]
    r2 = hrm.check_update("app", {"port": 8080, "debug": True})
    assert r2["changed"]
    assert r2["version"] == 2
    assert hrm.stats()["total_reloads"] == 1
