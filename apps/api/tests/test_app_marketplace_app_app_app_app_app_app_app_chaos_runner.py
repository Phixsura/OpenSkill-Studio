from app.services.app_marketplace_app_app_app_app_app_app_app_chaos_runner import ChaosRunner

def test_chaos():
    cr = ChaosRunner()
    exp = cr.create(name="Kill API pods", target="api", fault_type="pod_kill",
                     duration_sec=120, blast_radius_pct=25)
    assert exp["status"] == "created"
    cr.start(exp["id"])
    r = cr.complete(exp["id"], success=True, impact="Service recovered in 15s")
    assert r["success"]
    exps = cr.list_experiments()
    assert len(exps) == 1
    assert exps[0]["status"] == "completed"
    assert exps[0]["blast_radius_pct"] == 25
