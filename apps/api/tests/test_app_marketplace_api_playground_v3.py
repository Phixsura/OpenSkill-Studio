from app.services.app_marketplace_api_playground_v3 import create_collection, create_environment, interpolate_request

def test_collection():
    c = create_collection(name="Auth Flow", requests=[{"method": "POST", "path": "/login"}])
    assert c["request_count"] == 1

def test_env():
    e = create_environment(name="production", variables={"base_url": "https://api.com", "token": "abc"})
    assert e["variable_count"] == 2

def test_interpolate():
    r = interpolate_request(
        url="{{base_url}}/users", headers={"Authorization": "Bearer {{token}}"},
        body='{"org": "{{org_id}}"}', env={"base_url": "https://api.com", "token": "abc", "org_id": "org1"})
    assert r["url"] == "https://api.com/users"
    assert r["headers"]["Authorization"] == "Bearer abc"
    assert '"org": "org1"' in r["body"]
