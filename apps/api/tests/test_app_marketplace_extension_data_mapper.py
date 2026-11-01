from app.services.app_marketplace_extension_data_mapper import (
    DataMapperService,
)


def test_simple_rename():
    svc = DataMapperService()
    svc.create_mapping("m1", "Slack→Jira", "slack", "jira",
                       [{"source": "channel", "target": "project"}])
    result = svc.transform("m1", {"channel": "#general"})
    assert result == {"project": "#general"}


def test_nested_extract():
    svc = DataMapperService()
    svc.create_mapping("m1", "Map", "a", "b",
                       [{"source": "user.name", "target": "author"}])
    result = svc.transform("m1", {"user": {"name": "Alice"}})
    assert result == {"author": "Alice"}


def test_nested_set():
    svc = DataMapperService()
    svc.create_mapping("m1", "Map", "a", "b",
                       [{"source": "name", "target": "meta.author"}])
    result = svc.transform("m1", {"name": "Bob"})
    assert result == {"meta": {"author": "Bob"}}


def test_cast_transform():
    svc = DataMapperService()
    svc.create_mapping("m1", "Map", "a", "b",
                       [{"source": "count", "target": "total",
                         "transform": "cast", "config": {"type": "integer"}}])
    result = svc.transform("m1", {"count": "42"})
    assert result == {"total": 42}


def test_default_value():
    svc = DataMapperService()
    svc.create_mapping("m1", "Map", "a", "b",
                       [{"source": "missing", "target": "status",
                         "transform": "default", "config": {"default": "unknown"}}])
    result = svc.transform("m1", {})
    assert result == {"status": "unknown"}


def test_uppercase():
    svc = DataMapperService()
    svc.create_mapping("m1", "Map", "a", "b",
                       [{"source": "code", "target": "CODE", "transform": "uppercase"}])
    result = svc.transform("m1", {"code": "abc"})
    assert result == {"CODE": "ABC"}


def test_template():
    svc = DataMapperService()
    svc.create_mapping("m1", "Map", "a", "b",
                       [{"source": "id", "target": "url",
                         "transform": "template", "config": {"template": "https://api.example.com/{value}"}}])
    result = svc.transform("m1", {"id": "123"})
    assert result == {"url": "https://api.example.com/123"}


def test_batch_transform():
    svc = DataMapperService()
    svc.create_mapping("m1", "Map", "a", "b",
                       [{"source": "x", "target": "y"}])
    results = svc.transform_batch("m1", [{"x": 1}, {"x": 2}, {"x": 3}])
    assert len(results) == 3
    assert results[2] == {"y": 3}
