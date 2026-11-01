from app.services.app_marketplace_extension_sandbox_config_merge import (
    SandboxConfigMergeService, ArrayStrategy, ConflictStrategy,
)


def test_simple_merge():
    svc = SandboxConfigMergeService()
    result = svc.merge([{"a": 1}, {"b": 2}])
    assert result.merged == {"a": 1, "b": 2}
    assert result.sources_merged == 2


def test_deep_merge():
    svc = SandboxConfigMergeService()
    result = svc.merge([
        {"db": {"host": "localhost", "port": 5432}},
        {"db": {"port": 3306, "name": "mydb"}},
    ])
    assert result.merged["db"]["host"] == "localhost"
    assert result.merged["db"]["port"] == 3306
    assert result.merged["db"]["name"] == "mydb"


def test_last_wins():
    svc = SandboxConfigMergeService()
    result = svc.merge([{"theme": "light"}, {"theme": "dark"}],
                       conflict_strategy=ConflictStrategy.LAST_WINS)
    assert result.merged["theme"] == "dark"
    assert len(result.conflicts) == 1


def test_first_wins():
    svc = SandboxConfigMergeService()
    result = svc.merge([{"theme": "light"}, {"theme": "dark"}],
                       conflict_strategy=ConflictStrategy.FIRST_WINS)
    assert result.merged["theme"] == "light"


def test_array_replace():
    svc = SandboxConfigMergeService()
    result = svc.merge([{"tags": ["a", "b"]}, {"tags": ["c"]}],
                       array_strategy=ArrayStrategy.REPLACE)
    assert result.merged["tags"] == ["c"]


def test_array_append():
    svc = SandboxConfigMergeService()
    result = svc.merge([{"tags": ["a", "b"]}, {"tags": ["c"]}],
                       array_strategy=ArrayStrategy.APPEND)
    assert result.merged["tags"] == ["a", "b", "c"]


def test_array_unique():
    svc = SandboxConfigMergeService()
    result = svc.merge([{"tags": ["a", "b"]}, {"tags": ["b", "c"]}],
                       array_strategy=ArrayStrategy.UNIQUE)
    assert result.merged["tags"] == ["a", "b", "c"]


def test_three_sources():
    svc = SandboxConfigMergeService()
    result = svc.merge([
        {"a": 1, "b": 2},
        {"b": 3, "c": 4},
        {"c": 5, "d": 6},
    ])
    assert result.merged == {"a": 1, "b": 3, "c": 5, "d": 6}
    assert result.sources_merged == 3


def test_diff():
    svc = SandboxConfigMergeService()
    d = svc.diff({"a": 1, "b": 2, "c": 3}, {"b": 99, "c": 3, "d": 4})
    assert d["added"] == {"d": 4}
    assert d["removed"] == {"a": 1}
    assert d["changed"]["b"] == {"from": 2, "to": 99}


def test_empty_sources():
    svc = SandboxConfigMergeService()
    result = svc.merge([])
    assert result.merged == {}
