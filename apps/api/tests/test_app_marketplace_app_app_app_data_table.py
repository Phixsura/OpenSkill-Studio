from app.services.app_marketplace_app_app_app_data_table import build_data_table

COLS = [{"key": "name", "label": "Name"}, {"key": "downloads", "label": "Downloads"}]
ROWS = [{"name": "App A", "downloads": 500}, {"name": "App B", "downloads": 1000},
        {"name": "App C", "downloads": 200}]

def test_basic():
    r = build_data_table(columns=COLS, rows=ROWS)
    assert r["total"] == 3
    assert r["page"] == 1

def test_sort():
    r = build_data_table(columns=COLS, rows=ROWS, sort_by="downloads", sort_dir="desc")
    assert r["rows"][0]["name"] == "App B"

def test_pagination():
    r = build_data_table(columns=COLS, rows=ROWS, page=1, page_size=2)
    assert len(r["rows"]) == 2
    assert r["total_pages"] == 2
