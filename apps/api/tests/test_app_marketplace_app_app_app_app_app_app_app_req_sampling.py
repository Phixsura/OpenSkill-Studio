from app.services.app_marketplace_app_app_app_app_app_app_app_req_sampling import should_sample, sampling_stats

def test_high_priority():
    r = should_sample("req-1", 0.01, "high")
    assert r["sampled"]
    assert r["reason"] == "high_priority"

def test_error():
    r = should_sample("req-2", 0.01, "error")
    assert r["sampled"]

def test_rate():
    r = should_sample("req-3", 0.5, "normal")
    assert isinstance(r["sampled"], bool)

def test_stats():
    r = sampling_stats(10000, 1050, 0.1)
    assert r["actual_rate"] == 0.105
    assert r["dropped"] == 8950
