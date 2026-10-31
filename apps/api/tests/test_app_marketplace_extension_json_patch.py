from app.services.app_marketplace_extension_json_patch import JsonPatchEngineService, JsonPatchError
import pytest


def test_add():
    svc = JsonPatchEngineService()
    doc = {"name": "Alice"}
    result = svc.apply(doc, [{"op": "add", "path": "/age", "value": 30}])
    assert result == {"name": "Alice", "age": 30}


def test_remove():
    svc = JsonPatchEngineService()
    doc = {"name": "Alice", "age": 30}
    result = svc.apply(doc, [{"op": "remove", "path": "/age"}])
    assert result == {"name": "Alice"}


def test_replace():
    svc = JsonPatchEngineService()
    doc = {"name": "Alice"}
    result = svc.apply(doc, [{"op": "replace", "path": "/name", "value": "Bob"}])
    assert result == {"name": "Bob"}


def test_move():
    svc = JsonPatchEngineService()
    doc = {"first": "Alice", "last": "Smith"}
    result = svc.apply(doc, [{"op": "move", "from": "/first", "path": "/name"}])
    assert result == {"last": "Smith", "name": "Alice"}


def test_copy():
    svc = JsonPatchEngineService()
    doc = {"name": "Alice"}
    result = svc.apply(doc, [{"op": "copy", "from": "/name", "path": "/backup"}])
    assert result == {"name": "Alice", "backup": "Alice"}


def test_test_pass():
    svc = JsonPatchEngineService()
    doc = {"version": "1.0"}
    result = svc.apply(doc, [{"op": "test", "path": "/version", "value": "1.0"}])
    assert result == {"version": "1.0"}


def test_test_fail():
    svc = JsonPatchEngineService()
    doc = {"version": "1.0"}
    with pytest.raises(JsonPatchError, match="Test failed"):
        svc.apply(doc, [{"op": "test", "path": "/version", "value": "2.0"}])


def test_nested():
    svc = JsonPatchEngineService()
    doc = {"user": {"name": "Alice", "address": {"city": "NYC"}}}
    result = svc.apply(doc, [
        {"op": "replace", "path": "/user/address/city", "value": "LA"},
        {"op": "add", "path": "/user/address/zip", "value": "90001"},
    ])
    assert result["user"]["address"]["city"] == "LA"
    assert result["user"]["address"]["zip"] == "90001"


def test_array_operations():
    svc = JsonPatchEngineService()
    doc = {"tags": ["a", "b", "c"]}
    result = svc.apply(doc, [
        {"op": "add", "path": "/tags/-", "value": "d"},
        {"op": "remove", "path": "/tags/0"},
    ])
    assert result["tags"] == ["b", "c", "d"]


def test_diff():
    svc = JsonPatchEngineService()
    old = {"name": "Alice", "age": 30, "city": "NYC"}
    new = {"name": "Alice", "age": 31, "country": "US"}
    ops = svc.diff(old, new)
    assert any(o["op"] == "replace" and o["path"] == "/age" for o in ops)
    assert any(o["op"] == "remove" and o["path"] == "/city" for o in ops)
    assert any(o["op"] == "add" and o["path"] == "/country" for o in ops)


def test_diff_nested():
    svc = JsonPatchEngineService()
    old = {"user": {"name": "Alice", "age": 30}}
    new = {"user": {"name": "Alice", "age": 31}}
    ops = svc.diff(old, new)
    assert ops == [{"op": "replace", "path": "/user/age", "value": 31}]


def test_original_not_mutated():
    svc = JsonPatchEngineService()
    doc = {"name": "Alice"}
    svc.apply(doc, [{"op": "add", "path": "/age", "value": 30}])
    assert "age" not in doc  # original unchanged
