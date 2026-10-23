from app.services.app_marketplace_app_app_app_app_app_app_app_data_export import (
    create_export, list_exports, export_stats, clear_exports,
)

def test_create():
    clear_exports()
    r = create_export("users", "csv", row_count=5000)
    assert r["created"]
    assert r["size_mb"] == 5.0
    r2 = create_export("bad", "xml")
    assert not r2["created"]
    clear_exports()

def test_stats():
    clear_exports()
    create_export("a", "csv", row_count=1000)
    create_export("b", "json", row_count=2000)
    create_export("c", "csv", row_count=500)
    s = export_stats()
    assert s["total"] == 3
    assert s["by_format"]["csv"] == 2
    clear_exports()
