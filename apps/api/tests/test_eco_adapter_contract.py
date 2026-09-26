"""Round-59 killers (ADR-016 §56.2): adapter identity & event-type contracts."""

import json

from app.ecosystem.services.adapters import ADAPTERS, NormalizedItem


def test_raw_hash_is_key_order_independent():
    """Killer: the idempotency hash must be identical for the same content
    regardless of dict insertion order — otherwise the same payload would
    re-ingest as a duplicate observation whenever key order shifts."""
    a = NormalizedItem(event_type="model_released", entity_kind="model", external_ref="x", normalized={"b": 1, "a": 2})
    b = NormalizedItem(event_type="model_released", entity_kind="model", external_ref="x", normalized={"a": 2, "b": 1})
    assert a.raw_hash == b.raw_hash
    c = NormalizedItem(event_type="model_released", entity_kind="model", external_ref="x", normalized={"a": 2, "b": 999})
    assert c.raw_hash != a.raw_hash  # different content ⇒ different hash


def test_pricing_adapter_emits_price_changed():
    """Killer: the pricing adapter's items are price_changed — a drifted
    event type would route price facts around the pricing pipeline."""
    payload = json.dumps({
        "prices": [{"model": "acme-img", "unit": "image", "price": 0.04}]
    }).encode()
    items = ADAPTERS["pricing_json"].parse(payload, {})
    assert items, "pricing adapter parsed nothing"
    assert all(i.event_type == "price_changed" for i in items)


def test_huggingface_adapter_emits_model_released():
    """Killer: HF listings are model_released — the discovery pipeline keys
    resolution + change detection off this type."""
    payload = json.dumps([
        {"modelId": "acme/gen-3", "sha": "abc", "tags": ["text-to-image"]}
    ]).encode()
    items = ADAPTERS["huggingface"].parse(payload, {})
    assert items, "hf adapter parsed nothing"
    assert all(i.event_type == "model_released" for i in items)
