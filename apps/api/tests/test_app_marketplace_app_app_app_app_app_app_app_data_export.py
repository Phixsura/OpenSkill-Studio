from app.services.app_marketplace_app_app_app_app_app_app_app_data_export import DataExportManager

def test_lifecycle():
    dem = DataExportManager()
    dem.create("exp-1", "csv", "SELECT * FROM users", "admin")
    dem.complete("exp-1", 10000, 5242880)
    exports = dem.list_exports("completed")
    assert len(exports) == 1
    assert exports[0]["row_count"] == 10000

def test_fail():
    dem = DataExportManager()
    dem.create("exp-2", "json", "SELECT * FROM orders", "admin")
    dem.fail("exp-2", "timeout")
    s = dem.stats()
    assert s["by_status"]["failed"] == 1
