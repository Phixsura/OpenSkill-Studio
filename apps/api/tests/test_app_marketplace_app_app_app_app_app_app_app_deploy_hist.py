from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_hist import DeploymentHistory

def test_record():
    dh = DeploymentHistory()
    dh.record("1.0", "prod", "alice")
    dh.record("1.1", "prod", "bob", "failed")
    s = dh.stats()
    assert s["total"] == 2
    assert s["success_rate"] == 50.0
    assert len(dh.recent(env="prod")) == 2
