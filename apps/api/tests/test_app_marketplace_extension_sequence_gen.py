from app.services.app_marketplace_extension_sequence_gen import SequenceGeneratorService


def test_snowflake_unique():
    gen = SequenceGeneratorService(node_id=1)
    ids = [gen.snowflake() for _ in range(100)]
    assert len(set(ids)) == 100  # all unique


def test_snowflake_monotonic():
    gen = SequenceGeneratorService(node_id=1)
    ids = [gen.snowflake() for _ in range(100)]
    assert ids == sorted(ids)  # monotonically increasing


def test_snowflake_different_nodes():
    gen1 = SequenceGeneratorService(node_id=1)
    gen2 = SequenceGeneratorService(node_id=2)
    id1 = gen1.snowflake()
    id2 = gen2.snowflake()
    assert id1 != id2


def test_snowflake_decode():
    gen = SequenceGeneratorService(node_id=42)
    sf_id = gen.snowflake()
    decoded = gen.snowflake_decode(sf_id)
    assert decoded["node_id"] == 42
    assert decoded["sequence"] >= 0
    assert "T" in decoded["time_iso"]


def test_ulid_unique():
    gen = SequenceGeneratorService()
    ids = [gen.ulid() for _ in range(50)]
    assert len(set(ids)) == 50


def test_ulid_sortable():
    gen = SequenceGeneratorService()
    import time
    id1 = gen.ulid()
    time.sleep(0.002)
    id2 = gen.ulid()
    assert id1 < id2  # time-sortable


def test_prefixed():
    gen = SequenceGeneratorService()
    uid = gen.prefixed("user", 16)
    assert uid.startswith("user_")
    assert len(uid) == 5 + 16  # prefix_ + hex


def test_auto_increment():
    gen = SequenceGeneratorService()
    assert gen.auto_increment("orders") == 1
    assert gen.auto_increment("orders") == 2
    assert gen.auto_increment("users") == 1  # separate namespace


def test_batch():
    gen = SequenceGeneratorService(node_id=1)
    batch = gen.batch_snowflake(10)
    assert len(batch) == 10
    assert len(set(batch)) == 10  # all unique
    assert batch == sorted(batch)  # monotonic


def test_valid_snowflake():
    gen = SequenceGeneratorService(node_id=1)
    sf = gen.snowflake()
    assert gen.is_valid_snowflake(sf) is True
    assert gen.is_valid_snowflake(0) is False
    assert gen.is_valid_snowflake(-1) is False


def test_invalid_node():
    try:
        SequenceGeneratorService(node_id=2000)
        assert False
    except ValueError:
        pass
