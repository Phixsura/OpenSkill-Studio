from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_access_log import MeshAccessLog

def test_log_query():
    mal = MeshAccessLog()
    mal.log("web", "api", "GET", "/users", 200, 15)
    mal.log("api", "db", "SELECT", "users", 200, 5)
    mal.log("api", "db", "SELECT", "orders", 500, 100)
    errors = mal.query(status_gte=500)
    assert len(errors) == 1
    api_to_db = mal.query(source="api", destination="db")
    assert len(api_to_db) == 2
    s = mal.stats()
    assert s["total"] == 3
    assert s["errors"] == 1
