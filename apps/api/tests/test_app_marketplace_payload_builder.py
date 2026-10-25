from app.services.app_marketplace_payload_builder import (
    PayloadBuilder, PayloadRegistry,
)


def test_builder_fluent():
    payload = (PayloadBuilder("extension.installed")
        .set("extension_id", "ext-1")
        .set("org_id", "org-1")
        .meta("source", "api")
        .build())
    assert payload.event_type == "extension.installed"
    assert payload.data["extension_id"] == "ext-1"
    assert payload.metadata["source"] == "api"
    assert len(payload.idempotency_key) == 16


def test_set_many():
    payload = (PayloadBuilder("review.created")
        .set_many({"rating": 5, "author": "alice", "body": "Great!"})
        .build())
    assert payload.data["rating"] == 5
    assert payload.data["author"] == "alice"


def test_payload_has_timestamp():
    payload = PayloadBuilder("test.event").build()
    assert payload.timestamp != ""


def test_registry_validation():
    reg = PayloadRegistry()
    reg.register("install", ["extension_id", "org_id"], ["version"])
    payload = PayloadBuilder("install").set("extension_id", "e1").set("org_id", "o1").build()
    ok, warnings = reg.validate(payload)
    assert ok is True


def test_registry_missing_required():
    reg = PayloadRegistry()
    reg.register("install", ["extension_id", "org_id"])
    payload = PayloadBuilder("install").set("extension_id", "e1").build()
    ok, errors = reg.validate(payload)
    assert ok is False
    assert any("org_id" in e for e in errors)


def test_registry_unknown_field_warning():
    reg = PayloadRegistry()
    reg.register("install", ["extension_id"], ["org_id"])
    payload = PayloadBuilder("install").set("extension_id", "e1").set("extra", "val").build()
    ok, warnings = reg.validate(payload)
    assert ok is True
    assert any("Unknown" in w for w in warnings)


def test_list_event_types():
    reg = PayloadRegistry()
    reg.register("a.event", ["x"])
    reg.register("b.event", ["y"])
    assert reg.list_event_types() == ["a.event", "b.event"]
