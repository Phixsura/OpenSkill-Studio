from app.services.app_marketplace_app_app_app_app_app_app_app_cluster_node import create_node, cluster_summary

def test_node():
    n = create_node("node-1", 8, 32, "us-east-1a", 45, 60)
    assert n["status"] == "ready"
    n2 = create_node("node-2", 4, 16, "us-east-1b", 95, 85)
    assert n2["status"] == "pressure"

def test_summary():
    nodes = [
        create_node("n1", 8, 32, "zone-a", 40, 50),
        create_node("n2", 8, 32, "zone-a", 60, 70),
        create_node("n3", 4, 16, "zone-b", 92, 88),
    ]
    r = cluster_summary(nodes)
    assert r["node_count"] == 3
    assert r["ready"] == 2
    assert r["total_cpu_cores"] == 20
    assert r["by_zone"]["zone-a"] == 2
