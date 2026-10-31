from app.services.app_marketplace_app_app_app_app_app_app_app_api_compat import check_compatibility

def test_compatible():
    old = {"paths": {"/users": {"GET": {}}}}
    new = {"paths": {"/users": {"GET": {}}, "/health": {"GET": {}}}}
    r = check_compatibility(old, new)
    assert r["compatible"]
    assert r["compatible_count"] == 1

def test_breaking():
    old = {"paths": {"/users": {"GET": {}, "POST": {}}, "/old": {"GET": {}}}}
    new = {"paths": {"/users": {"GET": {}}}}
    r = check_compatibility(old, new)
    assert not r["compatible"]
    assert r["breaking_count"] == 2  # /old removed + POST removed
