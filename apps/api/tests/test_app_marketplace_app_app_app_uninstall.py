from app.services.app_marketplace_app_app_app_uninstall import build_uninstall_flow, confirm_uninstall

def test_uninstall_flow():
    r = build_uninstall_flow(app_name="SuperApp", app_id="a1",
                              data_sizes={"configuration": 10, "webhooks": 5, "cached_data": 200})
    assert r["app_name"] == "SuperApp"
    assert r["total_size_kb"] == 215
    assert len(r["data_to_remove"]) == 5
    assert "permanently deleted" in r["warning"]

def test_confirm():
    r = confirm_uninstall(app_id="a1")
    assert r["status"] == "uninstalled"
