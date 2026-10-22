from app.services.app_marketplace_app_analytics_export import export_to_csv, export_to_json, build_export_metadata

def test_csv():
    data = [{"date": "2026-01-01", "installs": 5}, {"date": "2026-01-02", "installs": 10}]
    csv_str = export_to_csv(data=data, columns=["date", "installs"])
    assert "date,installs" in csv_str
    assert "2026-01-01,5" in csv_str

def test_json():
    j = export_to_json(data=[{"x": 1}], pretty=True)
    assert '"count": 1' in j

def test_metadata():
    m = build_export_metadata(app_id="a1", export_type="csv", row_count=100, columns=["a", "b"])
    assert m["row_count"] == 100
    assert m["size_estimate_bytes"] > 0
