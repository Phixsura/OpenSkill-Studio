from app.services.app_marketplace_extension_gossip_protocol import (
    GossipProtocolService, NodeState
)


def test_join_cluster():
    g = GossipProtocolService("node-0")
    g.join("node-1")
    g.join("node-2")
    assert g.get_cluster_state()["total_nodes"] == 3
    assert g.get_cluster_state()["alive"] == 3


def test_gossip_round():
    g = GossipProtocolService("node-0", fanout=2)
    g.join("node-1")
    g.join("node-2")
    g.join("node-3")
    result = g.gossip_round(seed=42)
    assert result["peers_contacted"] == 2


def test_update_self():
    g = GossipProtocolService("node-0")
    state = g.update_self({"cpu": 45.0})
    assert state.metadata["cpu"] == 45.0
    assert state.version == 1


def test_receive_newer_state():
    g = GossipProtocolService("node-0")
    g.join("node-1")
    # Simulate receiving newer state from node-1
    remote = NodeState(node_id="node-1", version=5,
                       metadata={"role": "leader"})
    result = g.receive_state(remote)
    assert result == "updated"
    assert g.get_node("node-1").metadata["role"] == "leader"


def test_receive_stale_state():
    g = GossipProtocolService("node-0")
    g.join("node-1")
    # Set local version high
    g._states["node-1"].version = 10
    remote = NodeState(node_id="node-1", version=3)
    result = g.receive_state(remote)
    assert result == "stale"


def test_receive_new_node():
    g = GossipProtocolService("node-0")
    remote = NodeState(node_id="unknown-node", metadata={"new": True})
    result = g.receive_state(remote)
    assert result == "new"
    assert g.get_node("unknown-node") is not None


def test_suspect_and_confirm():
    g = GossipProtocolService("node-0")
    g.join("node-1")
    assert g.suspect_node("node-1") is True
    assert g.get_node("node-1").status == "suspect"
    assert g.confirm_dead("node-1") is True
    assert g.get_node("node-1").status == "dead"


def test_refute_suspicion():
    g = GossipProtocolService("node-0")
    g.join("node-1")
    g.suspect_node("node-1")
    g.refute_suspicion("node-1")
    assert g.get_node("node-1").status == "alive"
    assert g.get_node("node-1").version > 0


def test_dead_not_gossiped():
    g = GossipProtocolService("node-0", fanout=10)
    g.join("node-1")
    g.join("node-2")
    g._states["node-1"].status = "dead"
    result = g.gossip_round(seed=42)
    # Should only contact node-2 (alive)
    assert result["peers_contacted"] == 1


def test_alive_members():
    g = GossipProtocolService("node-0")
    g.join("node-1")
    g.join("node-2")
    g._states["node-2"].status = "dead"
    alive = g.get_alive_members()
    ids = {n.node_id for n in alive}
    assert "node-0" in ids
    assert "node-1" in ids
    assert "node-2" not in ids
