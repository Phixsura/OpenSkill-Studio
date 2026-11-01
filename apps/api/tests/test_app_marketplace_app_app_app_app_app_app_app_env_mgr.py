from app.services.app_marketplace_app_app_app_app_app_app_app_env_mgr import EnvironmentManager

def test_lifecycle():
    em = EnvironmentManager()
    em.create("staging", "standard", "us-east")
    em.provision("staging")
    em.deploy_service("staging", "api", "2.0.0")
    em.deploy_service("staging", "web", "3.0.0")
    em.create("prod", "premium", "us-east")
    em.provision("prod")
    r = em.promote("staging", "prod")
    assert r["services_promoted"] == 2
    envs = em.list_envs()
    assert len(envs) == 2
    assert envs[1]["services"] == 2
