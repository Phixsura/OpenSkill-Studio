from app.services.app_marketplace_app_app_app_export_data import build_export_manifest

def test_full_export():
    r = build_export_manifest(app={"id": "a1", "name": "SuperApp"})
    assert r["app_name"] == "SuperApp"
    assert r["total_sections"] == 6
    assert r["estimated_size_kb"] > 0

def test_partial():
    r = build_export_manifest(app={"id": "a1", "name": "X"}, include=["settings", "webhooks"])
    assert r["total_sections"] == 2
