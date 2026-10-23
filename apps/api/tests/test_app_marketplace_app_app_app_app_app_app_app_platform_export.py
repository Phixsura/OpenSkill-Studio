from app.services.app_marketplace_app_app_app_app_app_app_app_platform_export import export_platform_data, list_exportable_types

def test_json_export():
    r = export_platform_data(data_type="users", records=[{"id": "1", "name": "Alice"}], fmt="json")
    assert r["status"] == "completed"
    assert r["record_count"] == 1
    assert "Alice" in r["content"]

def test_csv_export():
    r = export_platform_data(data_type="apps", records=[{"id": "a1", "name": "MyApp"}], fmt="csv")
    assert r["status"] == "completed"
    assert "MyApp" in r["content"]

def test_ndjson():
    r = export_platform_data(data_type="logs", records=[{"event": "login"}, {"event": "logout"}], fmt="ndjson")
    assert r["record_count"] == 2
    assert r["content"].count("\n") == 1

def test_types():
    t = list_exportable_types()
    assert len(t) == 5
    assert any(x["type"] == "users" for x in t)
