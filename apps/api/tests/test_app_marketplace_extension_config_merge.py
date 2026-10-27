from app.services.app_marketplace_extension_config_merge import ConfigMergeService


def test_simple_merge():
    cm = ConfigMergeService()
    result = cm.merge(("defaults", {"a": 1}), ("custom", {"b": 2}))
    assert result.merged == {"a": 1, "b": 2}


def test_deep_merge():
    cm = ConfigMergeService()
    result = cm.merge(
        ("base", {"db": {"host": "localhost", "port": 5432}}),
        ("prod", {"db": {"host": "prod-db.internal"}}))
    assert result.merged["db"]["host"] == "prod-db.internal"
    assert result.merged["db"]["port"] == 5432  # preserved from base


def test_last_wins():
    cm = ConfigMergeService()
    result = cm.merge(
        ("a", {"x": 1}), ("b", {"x": 2}), ("c", {"x": 3}),
        strategy="last_wins")
    assert result.merged["x"] == 3


def test_first_wins():
    cm = ConfigMergeService()
    result = cm.merge(
        ("a", {"x": 1}), ("b", {"x": 2}),
        strategy="first_wins")
    assert result.merged["x"] == 1


def test_conflict_tracking():
    cm = ConfigMergeService()
    result = cm.merge(("a", {"x": 1}), ("b", {"x": 2}))
    assert len(result.conflicts) == 1
    assert result.conflicts[0]["path"] == "x"


def test_source_tracking():
    cm = ConfigMergeService()
    result = cm.merge(("defaults", {"a": 1}), ("env", {"b": 2}))
    assert result.sources["a"] == "defaults"
    assert result.sources["b"] == "env"


def test_array_replace():
    cm = ConfigMergeService()
    result = cm.merge(
        ("a", {"tags": [1, 2]}), ("b", {"tags": [3, 4]}),
        array_strategy="replace")
    assert result.merged["tags"] == [3, 4]


def test_array_append():
    cm = ConfigMergeService()
    result = cm.merge(
        ("a", {"tags": [1, 2]}), ("b", {"tags": [3, 4]}),
        array_strategy="append")
    assert result.merged["tags"] == [1, 2, 3, 4]


def test_array_unique():
    cm = ConfigMergeService()
    result = cm.merge(
        ("a", {"tags": [1, 2, 3]}), ("b", {"tags": [2, 3, 4]}),
        array_strategy="unique")
    assert result.merged["tags"] == [1, 2, 3, 4]


def test_type_safe():
    cm = ConfigMergeService()
    result = cm.merge(
        ("a", {"port": 8080}), ("b", {"port": "invalid"}),
        type_safe=True, strategy="error")
    assert result.merged["port"] == 8080  # kept old on type mismatch
    assert any(c["type"] == "type_mismatch" for c in result.conflicts)


def test_overlay():
    cm = ConfigMergeService()
    result = cm.overlay({"a": 1, "b": 2}, {"b": 3}, {"c": 4})
    assert result == {"a": 1, "b": 3, "c": 4}


def test_diff():
    cm = ConfigMergeService()
    diffs = cm.diff({"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 99, "d": 4})
    types = {d["path"]: d["type"] for d in diffs}
    assert types["b"] == "changed"
    assert types["c"] == "removed"
    assert types["d"] == "added"
