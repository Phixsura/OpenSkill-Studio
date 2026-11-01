from app.services.app_marketplace_app_resource_tagging import validate_tags, filter_by_tags, get_tag_cloud

def test_valid_tags():
    r = validate_tags(tags={"env": "production", "team": "backend"})
    assert r["valid"]

def test_invalid_key():
    r = validate_tags(tags={"BAD KEY!": "value"})
    assert not r["valid"]

def test_filter():
    resources = [
        {"id": "r1", "tags": {"env": "prod", "team": "api"}},
        {"id": "r2", "tags": {"env": "staging", "team": "api"}},
        {"id": "r3", "tags": {"env": "prod", "team": "web"}},
    ]
    r = filter_by_tags(resources=resources, required_tags={"env": "prod"})
    assert r["total_matched"] == 2

def test_cloud():
    resources = [{"tags": {"env": "prod"}}, {"tags": {"env": "prod"}}, {"tags": {"env": "staging"}}]
    r = get_tag_cloud(resources=resources)
    assert r["unique_keys"] == 1
    assert r["tag_keys"][0]["total"] == 3
