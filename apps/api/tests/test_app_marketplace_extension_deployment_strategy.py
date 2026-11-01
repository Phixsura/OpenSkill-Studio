from app.services.app_marketplace_extension_deployment_strategy import (
    DeploymentStrategyService, Strategy, DeployStatus,
)


def test_immediate_deploy():
    svc = DeploymentStrategyService()
    dep = svc.deploy("ext-1", "1.0", "2.0", Strategy.IMMEDIATE)
    assert dep.status == DeployStatus.COMPLETED
    assert dep.traffic_percent == 100
    assert svc.get_active_version("ext-1") == "2.0"


def test_canary_deploy():
    svc = DeploymentStrategyService()
    dep = svc.deploy("ext-1", "1.0", "2.0", Strategy.CANARY)
    assert dep.status == DeployStatus.IN_PROGRESS
    assert dep.traffic_percent == 5


def test_increase_traffic():
    svc = DeploymentStrategyService()
    dep = svc.deploy("ext-1", "1.0", "2.0", Strategy.CANARY)
    svc.increase_traffic(dep.deploy_id, 50)
    assert dep.traffic_percent == 50


def test_promote_requires_health():
    svc = DeploymentStrategyService()
    dep = svc.deploy("ext-1", "1.0", "2.0", Strategy.BLUE_GREEN)
    result = svc.promote(dep.deploy_id)
    assert result["ok"] is False  # health not passed


def test_promote_after_health():
    svc = DeploymentStrategyService()
    dep = svc.deploy("ext-1", "1.0", "2.0", Strategy.CANARY)
    svc.report_health(dep.deploy_id, True)
    result = svc.promote(dep.deploy_id)
    assert result["ok"] is True
    assert svc.get_active_version("ext-1") == "2.0"


def test_rollback():
    svc = DeploymentStrategyService()
    svc._active_version["ext-1"] = "1.0"
    dep = svc.deploy("ext-1", "1.0", "2.0", Strategy.CANARY)
    svc.report_health(dep.deploy_id, True)
    svc.promote(dep.deploy_id)
    result = svc.rollback(dep.deploy_id)
    assert result["ok"] is True
    assert svc.get_active_version("ext-1") == "1.0"


def test_rollback_unhealthy():
    svc = DeploymentStrategyService()
    dep = svc.deploy("ext-1", "1.0", "2.0", Strategy.CANARY)
    svc.report_health(dep.deploy_id, False, "High error rate")
    result = svc.rollback(dep.deploy_id)
    assert result["ok"] is True
    assert dep.status == DeployStatus.ROLLED_BACK


def test_blue_green():
    svc = DeploymentStrategyService()
    dep = svc.deploy("ext-1", "1.0", "2.0", Strategy.BLUE_GREEN)
    assert dep.traffic_percent == 0  # staging
    svc.report_health(dep.deploy_id, True)
    svc.promote(dep.deploy_id)
    assert dep.traffic_percent == 100
