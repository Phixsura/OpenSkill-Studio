from app.services.app_marketplace_app_multi_region import list_regions, deploy_to_region, get_region_health

def test_list():
    r = list_regions()
    assert len(r) == 4
    assert any(x["id"] == "us-east-1" for x in r)

def test_deploy():
    r = deploy_to_region(app_id="a1", version_id="v1", region="eu-west-1")
    assert r["status"] == "deploying"
    assert r["region_name"] == "Europe"

def test_deploy_invalid():
    r = deploy_to_region(app_id="a1", version_id="v1", region="mars-1")
    assert r["error"]

def test_health():
    deps = [{"region": "us-east-1", "status": "healthy"}, {"region": "eu-west-1", "status": "unhealthy"}]
    h = get_region_health(deployments=deps)
    assert h["global_status"] == "partial"
