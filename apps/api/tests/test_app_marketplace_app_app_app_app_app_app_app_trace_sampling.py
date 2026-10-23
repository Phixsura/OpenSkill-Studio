from app.services.app_marketplace_app_app_app_app_app_app_app_trace_sampling import TraceSampler

def test_sampling():
    s = TraceSampler(default_rate=0.1)
    s.add_rule(name="health", match_path="/health", rate=0.01)
    s.add_rule(name="api", match_path="/api/v1", rate=0.5)
    r1 = s.should_sample("/health", rand_val=0.005)
    assert r1["sampled"]
    assert r1["rule"] == "health"
    r2 = s.should_sample("/health", rand_val=0.5)
    assert not r2["sampled"]
    r3 = s.should_sample("/api/v1/users", rand_val=0.3)
    assert r3["sampled"]
    assert r3["rule"] == "api"
    r4 = s.should_sample("/other", rand_val=0.05)
    assert r4["sampled"]
    assert r4["rule"] == "default"
    assert s.summary()["total_rules"] == 2
