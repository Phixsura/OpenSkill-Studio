from app.services.app_marketplace_extension_error_codes import lookup, list_by_category, get_all

def test_lookup():
    ec = lookup("EXT_NOT_FOUND")
    assert ec is not None
    assert ec.http_status == 404

def test_list_by_category():
    sandbox = list_by_category("sandbox")
    assert any(c.code == "SANDBOX_LIMIT" for c in sandbox)

def test_get_all():
    assert len(get_all()) >= 8
