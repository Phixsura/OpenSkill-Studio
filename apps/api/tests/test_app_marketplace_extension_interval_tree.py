from app.services.app_marketplace_extension_interval_tree import IntervalTreeService


def test_point_query():
    tree = IntervalTreeService()
    tree.insert(1, 5, "A")
    tree.insert(3, 8, "B")
    tree.insert(10, 15, "C")
    results = tree.query_point(4)
    data = {i.data for i in results}
    assert data == {"A", "B"}


def test_point_no_match():
    tree = IntervalTreeService()
    tree.insert(1, 3)
    tree.insert(7, 9)
    assert tree.query_point(5) == []


def test_range_query():
    tree = IntervalTreeService()
    tree.insert(1, 5, "A")
    tree.insert(6, 10, "B")
    tree.insert(8, 15, "C")
    results = tree.query_range(4, 7)
    data = {i.data for i in results}
    assert data == {"A", "B"}  # A overlaps at 4-5, B overlaps at 6-7


def test_range_no_overlap():
    tree = IntervalTreeService()
    tree.insert(1, 3)
    tree.insert(10, 15)
    assert tree.query_range(5, 8) == []


def test_single_point_interval():
    tree = IntervalTreeService()
    tree.insert(5, 5, "point")
    assert len(tree.query_point(5)) == 1
    assert tree.query_point(4) == []


def test_many_intervals():
    tree = IntervalTreeService()
    for i in range(100):
        tree.insert(i * 2, i * 2 + 3, f"interval-{i}")
    assert tree.size == 100
    # Point 50 should be in several intervals
    results = tree.query_point(50)
    assert len(results) >= 2


def test_find_gaps():
    tree = IntervalTreeService()
    tree.insert(2, 4)
    tree.insert(7, 9)
    gaps = tree.find_gaps(0, 10)
    assert (0, 2) in gaps
    assert (4, 7) in gaps
    assert (9, 10) in gaps


def test_find_gaps_no_gaps():
    tree = IntervalTreeService()
    tree.insert(0, 10)
    gaps = tree.find_gaps(2, 8)
    assert gaps == []


def test_find_gaps_empty_range():
    tree = IntervalTreeService()
    gaps = tree.find_gaps(0, 100)
    assert gaps == [(0, 100)]


def test_invalid_interval():
    tree = IntervalTreeService()
    try:
        tree.insert(10, 5)
        assert False
    except ValueError:
        pass


def test_boundary_overlap():
    tree = IntervalTreeService()
    tree.insert(1, 5, "A")
    tree.insert(5, 10, "B")
    # Point 5 should match both
    results = tree.query_point(5)
    assert len(results) == 2
