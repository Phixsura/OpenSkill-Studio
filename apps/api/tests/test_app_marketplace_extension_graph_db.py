from app.services.app_marketplace_extension_graph_db import GraphDbService


def test_add_nodes_and_edges():
    g = GraphDbService()
    g.add_node("alice", "Person", {"age": 30})
    g.add_node("bob", "Person", {"age": 25})
    g.add_edge("alice", "bob", "KNOWS")
    assert g.stats() == {"nodes": 2, "edges": 1}


def test_neighbors():
    g = GraphDbService()
    g.add_node("a", "N"); g.add_node("b", "N"); g.add_node("c", "N")
    g.add_edge("a", "b", "LINK")
    g.add_edge("a", "c", "LINK")
    neighbors = g.neighbors("a")
    assert len(neighbors) == 2


def test_neighbor_filter():
    g = GraphDbService()
    g.add_node("a", "N"); g.add_node("b", "N"); g.add_node("c", "N")
    g.add_edge("a", "b", "FRIEND")
    g.add_edge("a", "c", "ENEMY")
    friends = g.neighbors("a", edge_label="FRIEND")
    assert len(friends) == 1
    assert friends[0][0] == "b"


def test_incoming_neighbors():
    g = GraphDbService()
    g.add_node("a", "N"); g.add_node("b", "N")
    g.add_edge("a", "b", "FOLLOWS")
    incoming = g.neighbors("b", direction="in")
    assert len(incoming) == 1
    assert incoming[0][0] == "a"


def test_bfs():
    g = GraphDbService()
    for i in range(5):
        g.add_node(str(i), "N")
    g.add_edge("0", "1", "E"); g.add_edge("0", "2", "E")
    g.add_edge("1", "3", "E"); g.add_edge("2", "4", "E")
    result = g.bfs("0")
    ids = [nid for nid, _ in result]
    assert "0" in ids and "3" in ids and "4" in ids


def test_bfs_max_depth():
    g = GraphDbService()
    for i in range(5):
        g.add_node(str(i), "N")
    g.add_edge("0", "1", "E"); g.add_edge("1", "2", "E")
    g.add_edge("2", "3", "E"); g.add_edge("3", "4", "E")
    result = g.bfs("0", max_depth=2)
    ids = [nid for nid, _ in result]
    assert "2" in ids
    assert "4" not in ids  # depth 4 > max_depth 2


def test_shortest_path():
    g = GraphDbService()
    for c in "ABCDE":
        g.add_node(c, "N")
    g.add_edge("A", "B", "R", weight=1)
    g.add_edge("B", "D", "R", weight=1)
    g.add_edge("A", "C", "R", weight=2)
    g.add_edge("C", "D", "R", weight=1)
    g.add_edge("D", "E", "R", weight=1)
    path, dist = g.shortest_path("A", "E")
    assert path == ["A", "B", "D", "E"]
    assert dist == 3.0


def test_no_path():
    g = GraphDbService()
    g.add_node("a", "N"); g.add_node("b", "N")
    path, dist = g.shortest_path("a", "b")
    assert path == []


def test_find_by_label():
    g = GraphDbService()
    g.add_node("a", "Person"); g.add_node("b", "Person"); g.add_node("c", "Company")
    assert len(g.find_by_label("Person")) == 2
