from app.services.app_developer_app_permissions_page_builder import build_permissions_page

def test_page():
    p = build_permissions_page(permissions=["read:cohorts", "write:projects", "subscribe:events"], manifest_permissions=[])
    assert p["read_count"] == 1
    assert p["write_count"] == 1
    assert p["special_count"] == 1
    assert p["total"] == 3
