from app.services.app_marketplace_app_app_data_export import export_to_csv, export_to_json, build_export_options

ROWS = [{"name": "App1", "downloads": 100}, {"name": "App2", "downloads": 500}]

def test_csv():
    r = export_to_csv(columns=["name", "downloads"], rows=ROWS)
    assert r["format"] == "csv"
    assert r["row_count"] == 2
    assert "App1" in r["content"]
    assert "name,downloads" in r["content"]

def test_json():
    r = export_to_json(rows=ROWS, pretty=True)
    assert r["format"] == "json"
    assert r["row_count"] == 2
    assert '"App1"' in r["content"]

def test_options():
    r = build_export_options(row_count=100, columns=["a", "b", "c"])
    assert len(r["formats"]) == 2
    assert r["column_count"] == 3
