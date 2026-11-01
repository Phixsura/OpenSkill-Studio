from app.services.app_marketplace_app_app_app_app_app_app_app_env_config import get_env_config, build_env_comparison, validate_deploy_target

def test_config():
    r = get_env_config("production")
    assert r["label"] == "Production"
    assert r["protected"]

def test_comparison():
    assert len(build_env_comparison()) == 3

def test_deploy():
    assert validate_deploy_target("staging")["allowed"]
    assert not validate_deploy_target("production")["allowed"]
    assert validate_deploy_target("production", has_approval=True)["allowed"]
