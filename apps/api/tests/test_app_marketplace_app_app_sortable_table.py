from app.services.app_marketplace_app_app_sortable_table import build_sortable_table

COLS = [{"key": "name", "label": "Name"}, {"key": "downloads", "label": "Downloads"}]
ROWS = [{"name": "Zapp", "downloads": 100}, {"name": "Alpha", "downloads": 500}]

def test_no_sort():
    r = build_sortable_table(columns=COLS, rows=ROWS)
    assert r["total_rows"] == 2
    assert r["rows"][0]["name"] == "Zapp"

def test_sort_asc():
    r = build_sortable_table(columns=COLS, rows=ROWS, sort_by="name", sort_dir="asc")
    assert r["rows"][0]["name"] == "Alpha"

def test_sort_desc():
    r = build_sortable_table(columns=COLS, rows=ROWS, sort_by="downloads", sort_dir="desc")
    assert r["rows"][0]["downloads"] == 500

def test_xss():
    rows = [{"name": "<script>alert(1)</script>", "downloads": 0}]
    r = build_sortable_table(columns=COLS, rows=rows)
    assert "<script>" not in r["rows"][0]["name"]
