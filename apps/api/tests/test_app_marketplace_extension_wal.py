from app.services.app_marketplace_extension_wal import WriteAheadLogService


def test_basic_transaction():
    wal = WriteAheadLogService()
    wal.begin("tx1")
    wal.write("tx1", "user:1", "Alice")
    wal.write("tx1", "user:2", "Bob")
    wal.commit("tx1")
    state = wal.get_state()
    assert state == {"user:1": "Alice", "user:2": "Bob"}


def test_abort_rolls_back():
    wal = WriteAheadLogService()
    wal.begin("tx1")
    wal.write("tx1", "key", "value")
    wal.abort("tx1")
    assert wal.get_state() == {}


def test_isolation():
    wal = WriteAheadLogService()
    wal.begin("tx1")
    wal.write("tx1", "a", "1")
    # tx1 not committed yet — state should be empty
    assert wal.get_state() == {}
    wal.commit("tx1")
    assert wal.get_state() == {"a": "1"}


def test_delete():
    wal = WriteAheadLogService()
    wal.begin("tx1")
    wal.write("tx1", "key", "value")
    wal.commit("tx1")
    wal.begin("tx2")
    wal.delete("tx2", "key")
    wal.commit("tx2")
    assert wal.get_state() == {}


def test_checkpoint_truncates_log():
    wal = WriteAheadLogService()
    wal.begin("tx1")
    wal.write("tx1", "a", "1")
    wal.commit("tx1")
    log_before = wal.get_log_size()
    wal.checkpoint()
    log_after = wal.get_log_size()
    assert log_after < log_before


def test_recovery_from_checkpoint():
    wal = WriteAheadLogService()
    wal.begin("tx1")
    wal.write("tx1", "a", "1")
    wal.commit("tx1")
    wal.checkpoint()
    # New transaction after checkpoint
    wal.begin("tx2")
    wal.write("tx2", "b", "2")
    wal.commit("tx2")
    # Simulate crash recovery
    recovered = wal.recover()
    assert recovered == {"a": "1", "b": "2"}


def test_recovery_skips_aborted():
    wal = WriteAheadLogService()
    wal.begin("tx1")
    wal.write("tx1", "good", "data")
    wal.commit("tx1")
    wal.begin("tx2")
    wal.write("tx2", "bad", "data")
    wal.abort("tx2")
    recovered = wal.recover()
    assert "good" in recovered
    assert "bad" not in recovered


def test_lsn_monotonic():
    wal = WriteAheadLogService()
    e1 = wal.begin("tx1")
    e2 = wal.write("tx1", "k", "v")
    e3 = wal.commit("tx1")
    assert e1.lsn < e2.lsn < e3.lsn


def test_concurrent_transactions():
    wal = WriteAheadLogService()
    wal.begin("tx1")
    wal.begin("tx2")
    wal.write("tx1", "a", "from-tx1")
    wal.write("tx2", "b", "from-tx2")
    wal.commit("tx1")
    wal.abort("tx2")
    state = wal.get_state()
    assert state == {"a": "from-tx1"}


def test_duplicate_tx_rejected():
    wal = WriteAheadLogService()
    wal.begin("tx1")
    try:
        wal.begin("tx1")
        assert False
    except ValueError:
        pass
