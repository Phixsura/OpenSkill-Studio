from app.services.app_marketplace_app_app_app_app_app_app_app_req_lifecycle import RequestLifecycle

def test_lifecycle():
    rl = RequestLifecycle()
    rl.start("req-1")
    rl.add_stage("req-1", "auth", 5)
    rl.add_stage("req-1", "validate", 2)
    rl.add_stage("req-1", "process", 50)
    rl.add_stage("req-1", "serialize", 3)
    r = rl.complete("req-1")
    assert r["total_ms"] == 60
    assert r["stages"] == 4
    assert r["success"]

def test_failure():
    rl = RequestLifecycle()
    rl.start("req-2")
    rl.add_stage("req-2", "auth", 5, "error")
    r = rl.complete("req-2")
    assert not r["success"]
