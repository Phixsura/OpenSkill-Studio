from app.services.app_marketplace_app_app_app_app_app_app_app_data_export import export_data

def test_csv_export():
    records = [{"name": "Alice", "plan": "pro"}, {"name": "Bob", "plan": "free"}]
    r = export_data(records, fmt="csv")
    assert r["status"] == "complete"
    assert r["rows"] == 2
    assert "Alice" in r["content"]
    assert r["format"] == "csv"

def test_json_export():
    records = [{"id": 1, "value": 42}]
    r = export_data(records, fmt="json", columns=["id", "value"])
    assert r["status"] == "complete"
    assert r["size_bytes"] > 0
    assert '"value": 42' in r["content"]

def test_empty():
    r = export_data([], fmt="csv")
    assert r["status"] == "empty"
    assert r["rows"] == 0
