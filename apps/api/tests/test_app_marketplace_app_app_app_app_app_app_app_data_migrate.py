from app.services.app_marketplace_app_app_app_app_app_app_app_data_migrate import plan_migration, validate_migration

def test_plan():
    r = plan_migration(
        {"name": "old-db"}, {"name": "new-db"},
        [{"name": "users", "row_count": 50000, "throughput": 10000},
         {"name": "orders", "row_count": 200000, "throughput": 50000}])
    assert r["total_rows"] == 250000
    assert r["steps"][0]["table"] == "orders"
    assert r["steps"][0]["strategy"] == "bulk"

def test_validate_ok():
    r = validate_migration({"users": 100, "orders": 200}, {"users": 100, "orders": 200})
    assert r["valid"]

def test_validate_mismatch():
    r = validate_migration({"users": 100}, {"users": 99})
    assert not r["valid"]
    assert r["mismatches"][0]["diff"] == -1
