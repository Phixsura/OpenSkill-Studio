from app.services.app_marketplace_extension_webhook_transformer import (
    WebhookTransformerService, FieldMapping
)


def test_simple_rename():
    wt = WebhookTransformerService()
    result = wt.transform({"first_name": "Alice"},
                          [FieldMapping("first_name", "name")])
    assert result == {"name": "Alice"}


def test_nested_source():
    wt = WebhookTransformerService()
    result = wt.transform({"user": {"email": "a@b.com"}},
                          [FieldMapping("user.email", "email")])
    assert result == {"email": "a@b.com"}


def test_nested_target():
    wt = WebhookTransformerService()
    result = wt.transform({"email": "a@b.com"},
                          [FieldMapping("email", "contact.email")])
    assert result == {"contact": {"email": "a@b.com"}}


def test_transform_uppercase():
    wt = WebhookTransformerService()
    result = wt.transform({"name": "alice"},
                          [FieldMapping("name", "name", transform="uppercase")])
    assert result == {"name": "ALICE"}


def test_transform_int():
    wt = WebhookTransformerService()
    result = wt.transform({"count": "42"},
                          [FieldMapping("count", "count", transform="int")])
    assert result == {"count": 42}


def test_template():
    wt = WebhookTransformerService()
    result = wt.transform(
        {"first": "Alice", "last": "Smith"},
        [FieldMapping("first", "full_name", transform="template:{{first}} {{last}}")])
    assert result == {"full_name": "Alice Smith"}


def test_default_value():
    wt = WebhookTransformerService()
    result = wt.transform({},
                          [FieldMapping("missing", "value", default="fallback")])
    assert result == {"value": "fallback"}


def test_condition_exists():
    wt = WebhookTransformerService()
    result = wt.transform({"a": 1},
                          [FieldMapping("a", "x", condition="exists"),
                           FieldMapping("b", "y", condition="exists")])
    assert result == {"x": 1}  # b doesn't exist


def test_condition_not_empty():
    wt = WebhookTransformerService()
    result = wt.transform({"a": "", "b": "hello"},
                          [FieldMapping("a", "x", condition="not_empty"),
                           FieldMapping("b", "y", condition="not_empty")])
    assert result == {"y": "hello"}


def test_flatten():
    wt = WebhookTransformerService()
    flat = wt.flatten({"user": {"name": "Alice", "address": {"city": "NYC"}}})
    assert flat == {"user.name": "Alice", "user.address.city": "NYC"}


def test_unflatten():
    wt = WebhookTransformerService()
    nested = wt.unflatten({"user.name": "Alice", "user.age": 30})
    assert nested == {"user": {"name": "Alice", "age": 30}}


def test_flatten_unflatten_roundtrip():
    wt = WebhookTransformerService()
    original = {"a": {"b": {"c": 1}, "d": 2}, "e": 3}
    assert wt.unflatten(wt.flatten(original)) == original
