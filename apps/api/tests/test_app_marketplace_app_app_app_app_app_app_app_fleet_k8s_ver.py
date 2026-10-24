from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_k8s_ver import fleet_k8s_version
def test_ver():
    r = fleet_k8s_version([{"k8s_version": "1.28"}, {"k8s_version": "1.29"}, {"k8s_version": "1.29"}])
    assert r["version_count"] == 2
    assert r["skewed"]
