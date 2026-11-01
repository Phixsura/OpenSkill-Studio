from app.services.app_marketplace_extension_cdc import CdcService


def test_capture_insert():
    cdc = CdcService()
    evt = cdc.capture_insert("users", "u1", {"name": "Alice", "age": 30})
    assert evt.operation == "INSERT"
    assert evt.after == {"name": "Alice", "age": 30}
    assert evt.before is None
    assert evt.sequence == 1


def test_capture_update():
    cdc = CdcService()
    evt = cdc.capture_update("users", "u1",
                             before={"name": "Alice", "age": 30},
                             after={"name": "Alice", "age": 31})
    assert evt.operation == "UPDATE"
    assert evt.changed_columns == ["age"]
    assert evt.before["age"] == 30
    assert evt.after["age"] == 31


def test_no_change_update():
    cdc = CdcService()
    evt = cdc.capture_update("users", "u1",
                             before={"name": "Alice"},
                             after={"name": "Alice"})
    assert evt is None  # no actual changes


def test_capture_delete():
    cdc = CdcService()
    evt = cdc.capture_delete("users", "u1", {"name": "Alice"})
    assert evt.operation == "DELETE"
    assert evt.before == {"name": "Alice"}
    assert evt.after is None


def test_consumer_poll_and_ack():
    cdc = CdcService()
    cdc.subscribe("etl-consumer")
    cdc.capture_insert("users", "u1", {"name": "Alice"})
    cdc.capture_insert("users", "u2", {"name": "Bob"})
    events = cdc.poll("etl-consumer")
    assert len(events) == 2
    cdc.ack("etl-consumer", events[-1].sequence)
    # No new events after ack
    assert len(cdc.poll("etl-consumer")) == 0


def test_filter_by_table():
    cdc = CdcService()
    cdc.subscribe("c1")
    cdc.capture_insert("users", "u1", {})
    cdc.capture_insert("orders", "o1", {})
    cdc.capture_insert("users", "u2", {})
    events = cdc.poll("c1", table="users")
    assert len(events) == 2


def test_filter_by_operation():
    cdc = CdcService()
    cdc.subscribe("c1")
    cdc.capture_insert("t", "k1", {"x": 1})
    cdc.capture_update("t", "k1", {"x": 1}, {"x": 2})
    cdc.capture_delete("t", "k1", {"x": 2})
    events = cdc.poll("c1", operations=["DELETE"])
    assert len(events) == 1


def test_key_history():
    cdc = CdcService()
    cdc.capture_insert("users", "u1", {"name": "Alice"})
    cdc.capture_update("users", "u1", {"name": "Alice"}, {"name": "Alicia"})
    cdc.capture_delete("users", "u1", {"name": "Alicia"})
    history = cdc.get_changes_for_key("users", "u1")
    assert len(history) == 3
    assert [e.operation for e in history] == ["INSERT", "UPDATE", "DELETE"]


def test_reconstruct_state():
    cdc = CdcService()
    cdc.capture_insert("users", "u1", {"name": "Alice"})
    cdc.capture_insert("users", "u2", {"name": "Bob"})
    cdc.capture_update("users", "u1", {"name": "Alice"}, {"name": "Alicia"})
    cdc.capture_delete("users", "u2", {"name": "Bob"})
    state = cdc.get_current_state("users")
    assert state == {"u1": {"name": "Alicia"}}


def test_monotonic_sequence():
    cdc = CdcService()
    e1 = cdc.capture_insert("t", "a", {})
    e2 = cdc.capture_insert("t", "b", {})
    e3 = cdc.capture_insert("t", "c", {})
    assert e1.sequence < e2.sequence < e3.sequence


def test_stats():
    cdc = CdcService()
    cdc.capture_insert("users", "u1", {})
    cdc.capture_update("users", "u1", {"x": 1}, {"x": 2})
    cdc.capture_insert("orders", "o1", {})
    stats = cdc.stats()
    assert stats["total_events"] == 3
    assert stats["by_table"]["users"] == 2
    assert stats["by_operation"]["INSERT"] == 2
