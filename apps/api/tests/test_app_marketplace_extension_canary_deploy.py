from app.services.app_marketplace_extension_canary_deploy import ExtCanaryDeployService

def test_create_and_route():
    svc = ExtCanaryDeployService()
    d = svc.create("ext-1", "1.0", "2.0", 50)
    v = svc.route(d.deploy_id, "user-1")
    assert v in ("1.0", "2.0")

def test_auto_rollback():
    svc = ExtCanaryDeployService()
    d = svc.create("ext-1", "1.0", "2.0", 100, error_threshold=5.0)
    # Simulate requests and errors
    for _ in range(10):
        svc.route(d.deploy_id, f"u-{_}")
    for _ in range(2):  # 2/10 = 20% > 5% threshold
        svc.report_error(d.deploy_id)
    assert d.status == "rolled_back"

def test_promote():
    svc = ExtCanaryDeployService()
    d = svc.create("ext-1", "1.0", "2.0", 50)
    svc.increase_rollout(d.deploy_id, 100)
    assert d.status == "completed"

def test_manual_rollback():
    svc = ExtCanaryDeployService()
    d = svc.create("ext-1", "1.0", "2.0")
    assert svc.rollback(d.deploy_id) is True
    assert d.status == "rolled_back"
