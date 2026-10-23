from app.services.app_marketplace_app_app_app_app_app_app_app_release_train import ReleaseTrainManager

def test_release_train():
    mgr = ReleaseTrainManager()
    t = mgr.create_train(version="3.5.0", services=[
        {"name": "api", "version": "3.5.0"},
        {"name": "web", "version": "3.5.0"},
        {"name": "worker", "version": "3.5.0"},
    ])
    mgr.approve_service(t["id"], "api")
    mgr.approve_service(t["id"], "web")
    r = mgr.approve_service(t["id"], "worker")
    assert r["train_ready"]
    s = mgr.status(t["id"])
    assert s["status"] == "ready"
    assert s["approved"] == 3
    rel = mgr.release(t["id"])
    assert rel["status"] == "released"
    assert rel["services_released"] == 3
