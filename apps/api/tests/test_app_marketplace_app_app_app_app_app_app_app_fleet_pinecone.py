from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pinecone import fleet_pinecone_status
def test_pc():
    r = fleet_pinecone_status([{"status": "Ready", "vector_count": 10000000, "qps": 1000}])
    assert r["vectors"] == 10000000
    assert r["all_ready"]
