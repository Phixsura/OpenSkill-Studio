from app.services.app_marketplace_app_app_app_app_app_app_app_graceful_shutdown import ShutdownCoordinator, plan_rolling_restart

def test_shutdown_flow():
    sc = ShutdownCoordinator(drain_seconds=15)
    sc.register_connection("c1", 1000)
    sc.register_connection("c2", 1001)
    assert sc.status()["state"] == "running"
    r = sc.initiate_shutdown()
    assert r["state"] == "draining"
    assert r["active_connections"] == 2
    r2 = sc.drain_complete()
    assert r2["state"] == "stopped"
    assert r2["ready_to_stop"]

def test_rolling_restart():
    batches = plan_rolling_restart(["i1", "i2", "i3", "i4", "i5"], batch_size=2)
    assert len(batches) == 3
    assert batches[0]["instances"] == ["i1", "i2"]
    assert batches[2]["size"] == 1
