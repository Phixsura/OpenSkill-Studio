from app.services.app_marketplace_app_app_app_app_app_app_app_sdk_gen import generate_sdk_metadata, sdk_coverage

def test_generate():
    r = generate_sdk_metadata([
        {"method": "GET", "path": "/api/v1/users", "params": ["limit", "offset"]},
        {"method": "POST", "path": "/api/v1/users"},
        {"method": "GET", "path": "/api/v1/orders"},
    ], sdk_name="openskill-sdk", version="1.0.0")
    assert r["total_methods"] == 3
    assert r["sdk_name"] == "openskill-sdk"

def test_coverage():
    r = sdk_coverage(
        [{"method": "GET", "path": "/users"}, {"method": "POST", "path": "/users"},
         {"method": "GET", "path": "/orders"}],
        ["GET /users", "POST /users"])
    assert r["covered"] == 2
    assert r["coverage_pct"] == 66.7
