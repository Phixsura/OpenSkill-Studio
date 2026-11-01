from app.services.app_marketplace_app_export_import import export_app_config, validate_import

def test_export():
    app = {"manifest": {"name": "MyApp"}, "settings": {"theme": "dark"}, "webhooks": []}
    r = export_app_config(app_id="a1", app=app, include=["manifest", "settings"])
    assert r["format_version"] == "1.0"
    assert "manifest" in r["data"]
    assert len(r["checksum"]) == 16

def test_invalid_section():
    r = export_app_config(app_id="a1", app={}, include=["magic"])
    assert "error" in r

def test_validate_ok():
    app = {"manifest": {"name": "X"}}
    exported = export_app_config(app_id="a1", app=app, include=["manifest"])
    r = validate_import(export_data=exported)
    assert r["valid"]

def test_validate_tampered():
    r = validate_import(export_data={"format_version": "1.0", "data": {"x": 1}, "checksum": "wrong"})
    assert not r["valid"]
    assert any("Checksum" in e for e in r["errors"])
