from app.services.app_marketplace_extension_bloom_gate import BloomGateService


def test_gate_blocks_absent():
    bg = BloomGateService()
    bg.create("users", expected=100)
    bg.populate("users", [f"user-{i}" for i in range(100)])
    # Existing user → should lookup
    assert bg.should_lookup("users", "user-50") is True
    # Non-existing → should NOT lookup (bloom says no)
    assert bg.should_lookup("users", "definitely-not-here") is False


def test_no_false_negatives():
    bg = BloomGateService()
    bg.create("ids", expected=1000)
    keys = [f"key-{i}" for i in range(500)]
    bg.populate("ids", keys)
    # Every added key MUST return True (no false negatives)
    for key in keys:
        assert bg.should_lookup("ids", key) is True


def test_savings_rate():
    bg = BloomGateService()
    bg.create("cache", expected=100, fpr=0.01)
    bg.populate("cache", [f"k-{i}" for i in range(100)])
    # Check many non-existing keys
    for i in range(1000):
        bg.should_lookup("cache", f"missing-{i}")
    stats = bg._gates["cache"].stats()
    assert stats["savings_rate"] > 90  # most non-existing keys filtered


def test_gate_or_lookup():
    bg = BloomGateService()
    bg.create("db", expected=10)
    bg.populate("db", ["alice", "bob"])
    # Existing → lookup called
    result, called = bg.gate_or_lookup("db", "alice", lambda k: {"name": k})
    assert called is True
    assert result["name"] == "alice"
    # Non-existing → lookup skipped
    result, called = bg.gate_or_lookup("db", "xyz", lambda k: {"name": k})
    assert called is False
    assert result is None


def test_rebuild():
    bg = BloomGateService()
    bg.create("old", expected=10)
    bg.populate("old", ["a", "b"])
    bg.rebuild("old", ["x", "y", "z"])
    assert bg.should_lookup("old", "x") is True
    assert bg.should_lookup("old", "a") is False  # old data gone


def test_composite_and():
    bg = BloomGateService()
    bg.create("set_a", expected=10)
    bg.create("set_b", expected=10)
    bg.populate("set_a", ["common", "only_a"])
    bg.populate("set_b", ["common", "only_b"])
    # AND: must be in both
    assert bg.composite_check(["set_a", "set_b"], "common", "and") is True
    assert bg.composite_check(["set_a", "set_b"], "only_a", "and") is False


def test_composite_or():
    bg = BloomGateService()
    bg.create("a", expected=10)
    bg.create("b", expected=10)
    bg.populate("a", ["x"])
    bg.populate("b", ["y"])
    assert bg.composite_check(["a", "b"], "x", "or") is True
    assert bg.composite_check(["a", "b"], "z", "or") is False


def test_no_gate():
    bg = BloomGateService()
    assert bg.should_lookup("nonexistent", "key") is True  # no gate = always lookup


def test_stats():
    bg = BloomGateService()
    bg.create("test", expected=100)
    bg.populate("test", ["a"])
    bg.should_lookup("test", "a")
    bg.should_lookup("test", "b")
    stats = bg.get_all_stats()
    assert "test" in stats
    assert stats["test"]["checks"] == 2
