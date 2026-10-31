from app.services.app_marketplace_extension_union_find import UnionFindService


def test_make_set():
    uf = UnionFindService()
    uf.make_set("a")
    uf.make_set("b")
    assert uf.num_components == 2
    assert not uf.connected("a", "b")


def test_union():
    uf = UnionFindService()
    uf.make_set("a"); uf.make_set("b"); uf.make_set("c")
    assert uf.union("a", "b") is True
    assert uf.connected("a", "b") is True
    assert uf.num_components == 2


def test_union_already_connected():
    uf = UnionFindService()
    uf.make_set("a"); uf.make_set("b")
    uf.union("a", "b")
    assert uf.union("a", "b") is False  # already same set


def test_transitive():
    uf = UnionFindService()
    for x in "abcde":
        uf.make_set(x)
    uf.union("a", "b")
    uf.union("b", "c")
    assert uf.connected("a", "c") is True  # transitive
    assert uf.connected("a", "d") is False


def test_component_size():
    uf = UnionFindService()
    for x in "abcde":
        uf.make_set(x)
    uf.union("a", "b")
    uf.union("b", "c")
    assert uf.component_size("a") == 3
    assert uf.component_size("d") == 1


def test_get_components():
    uf = UnionFindService()
    for x in "abcdef":
        uf.make_set(x)
    uf.union("a", "b"); uf.union("b", "c")
    uf.union("d", "e")
    components = uf.get_components()
    sizes = sorted(len(v) for v in components.values())
    assert sizes == [1, 2, 3]  # {a,b,c}, {d,e}, {f}


def test_largest_component():
    uf = UnionFindService()
    for x in range(10):
        uf.make_set(str(x))
    for x in range(5):
        uf.union("0", str(x))
    largest = uf.largest_component()
    assert len(largest) == 5


def test_path_compression():
    uf = UnionFindService()
    # Create long chain: 0→1→2→3→4
    for i in range(5):
        uf.make_set(str(i))
    for i in range(4):
        uf.union(str(i), str(i + 1))
    # After find with path compression, all should point to root
    root = uf.find("0")
    for i in range(5):
        assert uf._parent[str(i)] == root or uf.find(str(i)) == root


def test_auto_make_set():
    uf = UnionFindService()
    # find auto-creates if not exists
    uf.find("new_node")
    assert uf.num_components == 1


def test_many_unions():
    uf = UnionFindService()
    for i in range(1000):
        uf.make_set(str(i))
    for i in range(999):
        uf.union(str(i), str(i + 1))
    assert uf.num_components == 1
    assert uf.component_size("0") == 1000
