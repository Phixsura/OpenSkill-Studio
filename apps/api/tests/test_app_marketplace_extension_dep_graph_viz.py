from app.services.app_marketplace_extension_dep_graph_viz import DepGraphVizService


def test_simple_chain():
    viz = DepGraphVizService()
    nodes = {"a": "A", "b": "B", "c": "C"}
    edges = [("a", "b"), ("b", "c")]
    layout = viz.compute_layout(nodes, edges)
    assert layout.layers == 3
    layers = {n.node_id: n.layer for n in layout.nodes}
    assert layers["a"] < layers["b"] < layers["c"]


def test_diamond():
    viz = DepGraphVizService()
    nodes = {"root": "Root", "left": "Left", "right": "Right", "join": "Join"}
    edges = [("root", "left"), ("root", "right"), ("left", "join"), ("right", "join")]
    layout = viz.compute_layout(nodes, edges)
    layers = {n.node_id: n.layer for n in layout.nodes}
    assert layers["left"] == layers["right"]  # same layer
    assert layers["join"] > layers["left"]


def test_cycle_detection():
    viz = DepGraphVizService()
    nodes = {"a": "A", "b": "B"}
    edges = [("a", "b"), ("b", "a")]
    layout = viz.compute_layout(nodes, edges)
    assert layout.has_cycles is True
    back = [e for e in layout.edges if e.back_edge]
    assert len(back) >= 1


def test_independent_nodes():
    viz = DepGraphVizService()
    nodes = {"a": "A", "b": "B", "c": "C"}
    edges = []
    layout = viz.compute_layout(nodes, edges)
    assert layout.layers == 1  # all at layer 0
    assert layout.max_width == 3


def test_fan_in_out():
    viz = DepGraphVizService()
    nodes = {"hub": "Hub", "a": "A", "b": "B", "c": "C"}
    edges = [("a", "hub"), ("b", "hub"), ("c", "hub")]
    layout = viz.compute_layout(nodes, edges)
    hub = next(n for n in layout.nodes if n.node_id == "hub")
    assert hub.fan_in == 3
    assert hub.fan_out == 0


def test_metrics():
    viz = DepGraphVizService()
    nodes = {"a": "A", "b": "B", "c": "C", "d": "D"}
    edges = [("a", "c"), ("b", "c"), ("c", "d")]
    layout = viz.compute_layout(nodes, edges)
    metrics = viz.get_metrics(layout)
    assert metrics["nodes"] == 4
    assert metrics["edges"] == 3
    assert metrics["max_fan_in"] == 2
    assert "c" in metrics["bottleneck_nodes"]


def test_node_positions():
    viz = DepGraphVizService()
    nodes = {"a": "A", "b": "B"}
    edges = [("a", "b")]
    layout = viz.compute_layout(nodes, edges)
    for node in layout.nodes:
        assert node.x >= 0
        assert node.y >= 0
