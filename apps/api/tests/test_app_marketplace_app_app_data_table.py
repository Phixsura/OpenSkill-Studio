from app.services.app_marketplace_app_app_data_table import build_table_config

def test_basic():
    columns = [{"key": "name", "label": "Name"}, {"key": "installs", "label": "Installs"}]
    rows = [{"name": "App A", "installs": 500}, {"name": "App B", "installs": 1000},
            {"name": "App C", "installs": 200}]
    r = build_table_config(columns=columns, rows=rows)
    assert r["total_rows"] == 3
    assert r["total_pages"] == 1

def test_sort():
    rows = [{"name": "B"}, {"name": "A"}, {"name": "C"}]
    r = build_table_config(columns=[], rows=rows, sort_by="name", sort_dir="asc")
    assert r["rows"][0]["name"] == "A"

def test_pagination():
    rows = [{"id": i} for i in range(25)]
    r = build_table_config(columns=[], rows=rows, page=2, per_page=10)
    assert len(r["rows"]) == 10
    assert r["rows"][0]["id"] == 10
    assert r["total_pages"] == 3
