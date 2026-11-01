from app.services.app_marketplace_extension_api_schema_diff import ApiSchemaDiffService, ChangeKind


def test_added_field():
    svc = ApiSchemaDiffService()
    old = {"properties": {"name": {"type": "string"}}}
    new = {"properties": {"name": {"type": "string"}, "email": {"type": "string"}}}
    diffs = svc.diff_schemas(old, new)
    assert len(diffs) == 1
    assert diffs[0].kind == ChangeKind.ADDED
    assert diffs[0].breaking is False


def test_removed_field():
    svc = ApiSchemaDiffService()
    old = {"properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
    new = {"properties": {"name": {"type": "string"}}}
    diffs = svc.diff_schemas(old, new)
    removed = [d for d in diffs if d.kind == ChangeKind.REMOVED]
    assert len(removed) == 1
    assert removed[0].breaking is True


def test_type_change():
    svc = ApiSchemaDiffService()
    old = {"properties": {"count": {"type": "string"}}}
    new = {"properties": {"count": {"type": "integer"}}}
    diffs = svc.diff_schemas(old, new)
    assert diffs[0].kind == ChangeKind.TYPE_CHANGED
    assert diffs[0].breaking is True


def test_required_added_is_breaking():
    svc = ApiSchemaDiffService()
    old = {"properties": {"name": {"type": "string"}}, "required": []}
    new = {"properties": {"name": {"type": "string"}}, "required": ["name"]}
    diffs = svc.diff_schemas(old, new)
    req = [d for d in diffs if d.kind == ChangeKind.REQUIRED_ADDED]
    assert len(req) == 1
    assert req[0].breaking is True


def test_required_removed_is_non_breaking():
    svc = ApiSchemaDiffService()
    old = {"properties": {"name": {"type": "string"}}, "required": ["name"]}
    new = {"properties": {"name": {"type": "string"}}, "required": []}
    diffs = svc.diff_schemas(old, new)
    req = [d for d in diffs if d.kind == ChangeKind.REQUIRED_REMOVED]
    assert len(req) == 1
    assert req[0].breaking is False


def test_enum_removed_is_breaking():
    svc = ApiSchemaDiffService()
    old = {"properties": {"status": {"type": "string", "enum": ["active", "inactive", "deleted"]}}}
    new = {"properties": {"status": {"type": "string", "enum": ["active", "inactive"]}}}
    diffs = svc.diff_schemas(old, new)
    removed = [d for d in diffs if d.kind == ChangeKind.ENUM_REMOVED]
    assert len(removed) == 1
    assert removed[0].breaking is True


def test_enum_added_is_non_breaking():
    svc = ApiSchemaDiffService()
    old = {"properties": {"status": {"type": "string", "enum": ["active"]}}}
    new = {"properties": {"status": {"type": "string", "enum": ["active", "pending"]}}}
    diffs = svc.diff_schemas(old, new)
    added = [d for d in diffs if d.kind == ChangeKind.ENUM_ADDED]
    assert len(added) == 1
    assert added[0].breaking is False


def test_nested_object_diff():
    svc = ApiSchemaDiffService()
    old = {"properties": {"address": {"type": "object", "properties": {
        "city": {"type": "string"}, "zip": {"type": "string"}}}}}
    new = {"properties": {"address": {"type": "object", "properties": {
        "city": {"type": "string"}, "country": {"type": "string"}}}}}
    diffs = svc.diff_schemas(old, new)
    paths = {d.path for d in diffs}
    assert "address.zip" in paths  # removed
    assert "address.country" in paths  # added


def test_array_item_type_change():
    svc = ApiSchemaDiffService()
    old = {"properties": {"tags": {"type": "array", "items": {"type": "string"}}}}
    new = {"properties": {"tags": {"type": "array", "items": {"type": "integer"}}}}
    diffs = svc.diff_schemas(old, new)
    assert any(d.path == "tags[]" and d.kind == ChangeKind.TYPE_CHANGED for d in diffs)


def test_summarize():
    svc = ApiSchemaDiffService()
    old = {"properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
           "required": []}
    new = {"properties": {"a": {"type": "integer"}, "c": {"type": "string"}},
           "required": ["a"]}
    diffs = svc.diff_schemas(old, new)
    summary = svc.summarize(diffs)
    assert summary["total_changes"] > 0
    assert summary["breaking_count"] > 0
    assert summary["is_backward_compatible"] is False
    assert "a" in summary["breaking_paths"]


def test_no_changes():
    svc = ApiSchemaDiffService()
    schema = {"properties": {"id": {"type": "string"}, "name": {"type": "string"}}}
    diffs = svc.diff_schemas(schema, schema)
    assert len(diffs) == 0
    summary = svc.summarize(diffs)
    assert summary["is_backward_compatible"] is True
