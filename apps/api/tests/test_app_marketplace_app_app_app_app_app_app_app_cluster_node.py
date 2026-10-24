from app.services.app_marketplace_app_app_app_app_app_app_app_cluster_node import ClusterNodeManager

def test_lifecycle():
    cm = ClusterNodeManager()
    cm.add_node("n1", "worker", 8, 32)
    cm.add_node("n2", "worker", 16, 64)
    cm.cordon("n1")
    cm.drain("n1")
    cm.remove("n1")
    s = cm.stats()
    assert s["total_nodes"] == 1
    assert s["total_cpu"] == 16

def test_stats():
    cm = ClusterNodeManager()
    cm.add_node("n1", "control", 4, 16)
    cm.add_node("n2", "worker", 8, 32)
    s = cm.stats()
    assert s["ready"] == 2
    assert s["total_memory_gb"] == 48
