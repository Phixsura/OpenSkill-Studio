from app.services.app_marketplace_app_app_app_app_app_app_app_api_chlog_gen import diff_openapi, format_changelog

def test_diff():
    r = diff_openapi(
        {"paths": {"/users": {"get": {}}, "/orders": {"get": {}}}},
        {"paths": {"/users": {"get": {}, "post": {}}, "/products": {"get": {}}}})
    assert "/products" in r["added_paths"]
    assert "/orders" in r["removed_paths"]
    assert r["breaking"]
    assert r["total_changes"] == 3

def test_format():
    diff = {"added_paths": ["/products"], "removed_paths": ["/orders"],
            "modified_paths": [], "breaking": True, "total_changes": 2}
    text = format_changelog(diff, "v2.0")
    assert "## v2.0" in text
    assert "`/products`" in text
    assert "BREAKING" in text
