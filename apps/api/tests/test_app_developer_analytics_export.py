import json
from app.services.app_developer_analytics_export import export_as_json, export_as_csv, build_analytics_export

DATA = [{"date": "2026-01-01", "calls": 100}, {"date": "2026-01-02", "calls": 200}]

def test_json():
    j = export_as_json(DATA)
    parsed = json.loads(j)
    assert len(parsed) == 2

def test_csv():
    c = export_as_csv(DATA)
    assert "date" in c
    assert "100" in c

def test_csv_empty():
    assert export_as_csv([]) == ""

def test_build():
    r = build_analytics_export(app_name="X", period="2026-01", metrics=DATA)
    assert r["row_count"] == 2
    assert r["app_name"] == "X"
    assert len(r["json"]) > 0
    assert len(r["csv"]) > 0
