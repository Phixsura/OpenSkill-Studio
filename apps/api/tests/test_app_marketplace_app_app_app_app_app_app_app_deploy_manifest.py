from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_manifest import validate_manifest, diff_manifests

def test_valid():
    r = validate_manifest({"name": "myapp", "version": "1.0",
                           "services": [{"name": "api", "image": "api:1.0", "replicas": 2}]})
    assert r["valid"]

def test_invalid():
    r = validate_manifest({"version": "1.0", "services": [{"name": "api"}]})
    assert not r["valid"]
    assert len(r["errors"]) == 2  # missing name + missing image

def test_diff():
    r = diff_manifests(
        {"services": [{"name": "api", "image": "api:1.0"}, {"name": "old", "image": "old:1"}]},
        {"services": [{"name": "api", "image": "api:2.0"}, {"name": "new", "image": "new:1"}]})
    assert "new" in r["added"]
    assert "old" in r["removed"]
    assert r["changed"][0]["new_image"] == "api:2.0"
