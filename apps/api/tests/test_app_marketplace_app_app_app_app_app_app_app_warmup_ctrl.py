from app.services.app_marketplace_app_app_app_app_app_app_app_warmup_ctrl import WarmupController

def test_warmup():
    wc = WarmupController()
    wc.register("api", ["load_config", "init_db", "cache_warmup"])
    assert not wc.is_warm("api")
    r = wc.warmup("api")
    assert r["steps_completed"] == 3
    assert wc.is_warm("api")

def test_cold():
    wc = WarmupController()
    wc.register("api", ["a"])
    wc.register("worker", ["b"])
    wc.warmup("api")
    assert wc.cold_services() == ["worker"]
    assert wc.stats()["warm"] == 1
