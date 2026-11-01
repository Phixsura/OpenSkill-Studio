from app.services.app_marketplace_extension_trace_propagator import TracePropagatorService


def test_new_context():
    tp = TracePropagatorService()
    ctx = tp.new_context()
    assert len(ctx.trace_id) == 32
    assert len(ctx.parent_id) == 16
    assert ctx.sampled is True


def test_traceparent_format():
    tp = TracePropagatorService()
    ctx = tp.new_context()
    header = ctx.to_traceparent()
    parts = header.split("-")
    assert len(parts) == 4
    assert parts[0] == "00"  # version
    assert len(parts[1]) == 32  # trace_id
    assert len(parts[2]) == 16  # parent_id
    assert parts[3] in ("00", "01")  # flags


def test_inject_extract_roundtrip():
    tp = TracePropagatorService()
    original = tp.new_context(baggage={"user_id": "123", "tenant": "acme"})
    headers = tp.inject(original)
    extracted = tp.extract(headers)
    assert extracted is not None
    assert extracted.trace_id == original.trace_id
    assert extracted.parent_id == original.parent_id
    assert extracted.flags == original.flags
    assert extracted.baggage["user_id"] == "123"


def test_child_preserves_trace_id():
    tp = TracePropagatorService()
    parent = tp.new_context()
    child = tp.child_context(parent)
    assert child.trace_id == parent.trace_id
    assert child.parent_id != parent.parent_id  # new span ID


def test_child_inherits_baggage():
    tp = TracePropagatorService()
    parent = tp.new_context(baggage={"env": "prod"})
    child = tp.child_context(parent)
    assert child.baggage["env"] == "prod"


def test_unsampled():
    tp = TracePropagatorService()
    ctx = tp.new_context(sampled=False)
    assert ctx.sampled is False
    assert ctx.to_traceparent().endswith("-00")


def test_extract_invalid():
    tp = TracePropagatorService()
    assert tp.extract({}) is None
    assert tp.extract({"traceparent": "invalid"}) is None
    assert tp.extract({"traceparent": "01-abc-def-00"}) is None  # wrong version


def test_propagate():
    tp = TracePropagatorService()
    incoming = tp.inject(tp.new_context(baggage={"req_id": "r1"}))
    outgoing = tp.propagate(incoming, baggage_additions={"hop": "2"})
    # Outgoing has traceparent
    assert "traceparent" in outgoing
    # Extract and verify
    ctx = tp.extract(outgoing)
    # Same trace_id as incoming
    incoming_ctx = tp.extract(incoming)
    assert ctx.trace_id == incoming_ctx.trace_id
    # Baggage merged
    assert ctx.baggage["req_id"] == "r1"
    assert ctx.baggage["hop"] == "2"


def test_propagate_no_incoming():
    tp = TracePropagatorService()
    outgoing = tp.propagate({})
    assert "traceparent" in outgoing
    ctx = tp.extract(outgoing)
    assert ctx is not None  # new root context created
