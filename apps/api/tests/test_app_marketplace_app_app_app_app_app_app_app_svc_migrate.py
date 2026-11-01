from app.services.app_marketplace_app_app_app_app_app_app_app_svc_migrate import ServiceMigrationTracker

def test_migration():
    smt = ServiceMigrationTracker()
    smt.start("api", "heroku", "kubernetes")
    smt.set_steps("api", ["containerize", "deploy", "cutover", "decommission"])
    smt.complete_step("api")
    smt.complete_step("api")
    r = smt.complete_step("api")
    assert r["status"] == "in_progress"
    assert r["progress_pct"] == 75
    smt.complete_step("api")
    s = smt.summary()
    assert s["completed"] == 1
