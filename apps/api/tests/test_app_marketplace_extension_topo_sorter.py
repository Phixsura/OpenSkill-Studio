from app.services.app_marketplace_extension_topo_sorter import TopologySorterService


def test_linear_sort():
    ts = TopologySorterService()
    ts.add_edge("c", "b")
    ts.add_edge("b", "a")
    result = ts.sort()
    assert result.index("a") < result.index("b") < result.index("c")


def test_diamond_sort():
    ts = TopologySorterService()
    ts.add_edge("d", "b")
    ts.add_edge("d", "c")
    ts.add_edge("b", "a")
    ts.add_edge("c", "a")
    result = ts.sort()
    assert result.index("a") < result.index("b")
    assert result.index("a") < result.index("c")
    assert result.index("b") < result.index("d")


def test_cycle_detected():
    ts = TopologySorterService()
    ts.add_edge("a", "b")
    ts.add_edge("b", "a")
    assert ts.has_cycle() is True


def test_all_orderings():
    ts = TopologySorterService()
    ts.add_node("a")
    ts.add_node("b")
    ts.add_edge("c", "a")
    ts.add_edge("c", "b")
    orderings = ts.all_orderings()
    # a,b can be in any order, c must be last
    assert len(orderings) >= 2
    for order in orderings:
        assert order[-1] == "c"


def test_depth():
    ts = TopologySorterService()
    ts.add_node("root")
    ts.add_edge("mid", "root")
    ts.add_edge("leaf", "mid")
    assert ts.get_depth("root") == 0
    assert ts.get_depth("mid") == 1
    assert ts.get_depth("leaf") == 2


def test_layers():
    ts = TopologySorterService()
    ts.add_node("a")
    ts.add_node("b")
    ts.add_edge("c", "a")
    ts.add_edge("d", "b")
    ts.add_edge("e", "c")
    ts.add_edge("e", "d")
    layers = ts.get_layers()
    assert layers[0] == ["a", "b"]  # depth 0
    assert layers[1] == ["c", "d"]  # depth 1
    assert layers[2] == ["e"]       # depth 2


def test_transitive_reduction():
    ts = TopologySorterService()
    ts.add_edge("c", "a")
    ts.add_edge("c", "b")
    ts.add_edge("b", "a")
    # c→a is redundant because c→b→a
    redundant = ts.transitive_reduction()
    assert ("c", "a") in redundant


def test_no_deps():
    ts = TopologySorterService()
    ts.add_node("x")
    ts.add_node("y")
    ts.add_node("z")
    result = ts.sort()
    assert len(result) == 3
    assert ts.get_depth("x") == 0
