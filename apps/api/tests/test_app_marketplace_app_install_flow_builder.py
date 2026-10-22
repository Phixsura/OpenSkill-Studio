from app.services.app_marketplace_app_install_flow_builder import build_install_flow_page

def test_quick():
    p = build_install_flow_page(app={"name": "X", "slug": "x"}, permissions=[], org={"name": "O", "id": "1"}, config_schema=None, quick_install=True)
    assert p["flow_type"] == "quick"
    assert p["has_config"] is False

def test_standard():
    p = build_install_flow_page(app={"name": "X"}, permissions=["read:cohorts"], org={"name": "O", "id": "1"}, config_schema={"type": "object"}, quick_install=False)
    assert p["flow_type"] == "standard"
    assert p["has_config"] is True
