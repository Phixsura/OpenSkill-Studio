from app.services.app_marketplace_app_app_app_app_deploy_page import build_deploy_page, start_deployment

def test_deploy_page():
    r = build_deploy_page(app_name="SuperApp", versions=["2.0.0", "1.5.0"],
                           current_deploys={"production": "2.0.0", "staging": "2.0.0"})
    assert r["app_name"] == "SuperApp"
    assert r["deployed_count"] == 2
    assert len(r["environments"]) == 3

def test_start():
    r = start_deployment(app_id="a1", version="2.0.0", environment="production")
    assert r["deploy_id"].startswith("dep_")
    assert r["status"] == "deploying"

def test_bad_env():
    r = start_deployment(app_id="a1", version="1.0", environment="invalid")
    assert "error" in r
