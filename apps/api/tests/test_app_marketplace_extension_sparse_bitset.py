from app.services.app_marketplace_extension_sparse_bitset import SparseBitset


def test_set_test_clear():
    bs = SparseBitset()
    bs.set(42)
    assert bs.test(42) is True
    assert bs.test(43) is False
    bs.clear(42)
    assert bs.test(42) is False


def test_cardinality():
    bs = SparseBitset()
    bs.set(1)
    bs.set(100)
    bs.set(10000)
    assert bs.cardinality == 3


def test_toggle():
    bs = SparseBitset()
    assert bs.toggle(5) is True  # off → on
    assert bs.toggle(5) is False  # on → off


def test_large_sparse_values():
    bs = SparseBitset()
    bs.set(0)
    bs.set(1_000_000)
    bs.set(999_999_999)
    assert bs.cardinality == 3
    assert bs.test(1_000_000) is True
    # Only 3 chunks allocated, not millions
    assert bs.memory_bytes() < 100


def test_iter_set_bits():
    bs = SparseBitset()
    for bit in [100, 5, 50, 200]:
        bs.set(bit)
    assert bs.iter_set_bits() == [5, 50, 100, 200]


def test_union():
    a = SparseBitset()
    b = SparseBitset()
    a.set(1); a.set(2); a.set(3)
    b.set(2); b.set(3); b.set(4)
    u = a.union(b)
    assert u.iter_set_bits() == [1, 2, 3, 4]


def test_intersection():
    a = SparseBitset()
    b = SparseBitset()
    a.set(1); a.set(2); a.set(3)
    b.set(2); b.set(3); b.set(4)
    i = a.intersection(b)
    assert i.iter_set_bits() == [2, 3]


def test_difference():
    a = SparseBitset()
    b = SparseBitset()
    a.set(1); a.set(2); a.set(3)
    b.set(2); b.set(3); b.set(4)
    d = a.difference(b)
    assert d.iter_set_bits() == [1]


def test_xor():
    a = SparseBitset()
    b = SparseBitset()
    a.set(1); a.set(2)
    b.set(2); b.set(3)
    x = a.xor(b)
    assert x.iter_set_bits() == [1, 3]


def test_duplicate_set():
    bs = SparseBitset()
    bs.set(10)
    bs.set(10)
    assert bs.cardinality == 1  # not 2
