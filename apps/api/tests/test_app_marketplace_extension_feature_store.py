from app.services.app_marketplace_extension_feature_store import FeatureStoreService
import time


def test_register_and_ingest():
    fs = FeatureStoreService()
    fs.register_group("user_features", "user_id", [
        ("age", "int", "User age"),
        ("spend", "float", "Total spend"),
    ])
    fs.ingest("user_features", "u1", {"age": 30, "spend": 150.0})
    result = fs.get_online("user_features", "u1")
    assert result == {"age": 30, "spend": 150.0}


def test_latest_wins_online():
    fs = FeatureStoreService()
    fs.register_group("uf", "uid", [("score", "float", "")])
    fs.ingest("uf", "u1", {"score": 1.0}, event_time=100)
    fs.ingest("uf", "u1", {"score": 5.0}, event_time=200)
    fs.ingest("uf", "u1", {"score": 3.0}, event_time=150)  # older
    assert fs.get_online("uf", "u1") == {"score": 5.0}


def test_point_in_time():
    fs = FeatureStoreService()
    fs.register_group("uf", "uid", [("score", "float", "")])
    fs.ingest("uf", "u1", {"score": 1.0}, event_time=100)
    fs.ingest("uf", "u1", {"score": 5.0}, event_time=200)
    fs.ingest("uf", "u1", {"score": 9.0}, event_time=300)
    # As of time 150, score should be 1.0
    assert fs.get_point_in_time("uf", "u1", 150) == {"score": 1.0}
    # As of time 250, score should be 5.0
    assert fs.get_point_in_time("uf", "u1", 250) == {"score": 5.0}


def test_no_future_leakage():
    fs = FeatureStoreService()
    fs.register_group("uf", "uid", [("val", "float", "")])
    fs.ingest("uf", "u1", {"val": 999}, event_time=1000)
    # Looking up at time 500 should NOT see the time-1000 value
    assert fs.get_point_in_time("uf", "u1", 500) is None


def test_batch_retrieval():
    fs = FeatureStoreService()
    fs.register_group("uf", "uid", [("x", "float", "")])
    fs.ingest("uf", "u1", {"x": 1.0})
    fs.ingest("uf", "u2", {"x": 2.0})
    fs.ingest("uf", "u3", {"x": 3.0})
    batch = fs.get_batch("uf", ["u1", "u3", "u99"])
    assert len(batch) == 2
    assert batch["u1"]["x"] == 1.0


def test_feature_stats():
    fs = FeatureStoreService()
    fs.register_group("uf", "uid", [("score", "float", "")])
    for i in range(100):
        fs.ingest("uf", f"u{i}", {"score": float(i)})
    stats = fs.compute_stats("uf", "score")
    assert stats["count"] == 100
    assert stats["mean"] == 49.5
    assert stats["min"] == 0
    assert stats["max"] == 99


def test_drift_detection():
    fs = FeatureStoreService()
    fs.register_group("uf", "uid", [("val", "float", "")])
    # Current data centered at 50
    for i in range(50):
        fs.ingest("uf", f"u{i}", {"val": 50.0 + i * 0.1})
    # Reference was centered at 10 with stddev 5
    result = fs.detect_drift("uf", "val", reference_mean=10.0, reference_stddev=5.0)
    assert result["drifted"] is True
    assert result["z_score"] > 2


def test_no_drift():
    fs = FeatureStoreService()
    fs.register_group("uf", "uid", [("val", "float", "")])
    for i in range(50):
        fs.ingest("uf", f"u{i}", {"val": 10.0 + i * 0.01})
    result = fs.detect_drift("uf", "val", reference_mean=10.25, reference_stddev=5.0)
    assert result["drifted"] is False


def test_list_groups():
    fs = FeatureStoreService()
    fs.register_group("users", "uid", [("a", "int", "")])
    fs.register_group("items", "iid", [("b", "float", ""), ("c", "string", "")])
    fs.ingest("users", "u1", {"a": 1})
    groups = fs.list_groups()
    assert len(groups) == 2
    user_group = next(g for g in groups if g["group_id"] == "users")
    assert user_group["entities"] == 1
    assert user_group["features"] == 1
