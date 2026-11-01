from app.services.app_marketplace_app_app_app_app_app_app_app_data_table import build_table

def test_table():
    rows = [{"name": f"item-{i}", "value": i} for i in range(50)]
    r = build_table(rows=rows, columns=["name", "value"], page=1, page_size=10)
    assert len(r["rows"]) == 10
    assert r["total_rows"] == 50
    assert r["total_pages"] == 5
    assert r["has_next"]
    assert not r["has_prev"]

def test_sort_filter():
    rows = [{"name": "Banana", "price": 2}, {"name": "Apple", "price": 3}, {"name": "Cherry", "price": 1}]
    r = build_table(rows=rows, columns=["name", "price"], sort_by="price", sort_dir="asc")
    assert r["rows"][0]["name"] == "Cherry"
    r2 = build_table(rows=rows, columns=["name", "price"], filter_col="name", filter_val="app")
    assert r2["total_rows"] == 1
