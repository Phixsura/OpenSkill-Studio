from app.services.app_marketplace_extension_astar_search import AStarSearchService


def _grid_graph():
    """Create a 5x5 grid graph for testing."""
    g = AStarSearchService()
    for x in range(5):
        for y in range(5):
            g.add_node(f"{x},{y}", float(x), float(y))
    for x in range(5):
        for y in range(5):
            if x + 1 < 5: g.add_edge(f"{x},{y}", f"{x+1},{y}", 1.0)
            if y + 1 < 5: g.add_edge(f"{x},{y}", f"{x},{y+1}", 1.0)
    return g


def test_astar_finds_path():
    g = _grid_graph()
    result = g.search("0,0", "4,4")
    assert len(result.path) > 0
    assert result.path[0] == "0,0"
    assert result.path[-1] == "4,4"
    assert result.cost == 8.0  # Manhattan distance on grid


def test_astar_optimal():
    g = AStarSearchService()
    g.add_node("A"); g.add_node("B"); g.add_node("C"); g.add_node("D")
    g.add_edge("A", "B", 1)
    g.add_edge("B", "D", 1)
    g.add_edge("A", "C", 5)
    g.add_edge("C", "D", 1)
    result = g.search("A", "D")
    assert result.cost == 2.0  # A→B→D, not A→C→D


def test_no_path():
    g = AStarSearchService()
    g.add_node("A"); g.add_node("B")
    # No edges
    result = g.search("A", "B")
    assert result.path == []
    assert result.cost == float('inf')


def test_astar_fewer_nodes_than_dijkstra():
    g = _grid_graph()
    astar = g.search("0,0", "4,4", heuristic="manhattan")
    dijkstra = g.dijkstra("0,0", "4,4")
    # Both find optimal path
    assert astar.cost == dijkstra.cost
    # A* typically explores fewer nodes
    assert astar.nodes_explored <= dijkstra.nodes_explored


def test_dijkstra():
    g = AStarSearchService()
    g.add_node("A"); g.add_node("B"); g.add_node("C")
    g.add_edge("A", "B", 2)
    g.add_edge("B", "C", 3)
    g.add_edge("A", "C", 10)
    result = g.dijkstra("A", "C")
    assert result.cost == 5.0  # A→B→C


def test_find_nearest():
    g = _grid_graph()
    result = g.find_nearest("0,0", ["4,4", "1,1", "3,3"])
    assert result.path[-1] == "1,1"  # closest
    assert result.cost == 2.0


def test_weighted_edges():
    g = AStarSearchService()
    g.add_node("A"); g.add_node("B"); g.add_node("C")
    g.add_edge("A", "B", 100)
    g.add_edge("A", "C", 1)
    g.add_edge("C", "B", 1)
    result = g.search("A", "B")
    assert result.cost == 2.0  # A→C→B cheaper than A→B


def test_self_path():
    g = AStarSearchService()
    g.add_node("A")
    result = g.search("A", "A")
    assert result.path == ["A"]
    assert result.cost == 0
