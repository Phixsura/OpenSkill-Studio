from app.services.app_marketplace_app_app_app_app_app_app_app_req_sampling import RequestSampler

def test_sampling():
    rs = RequestSampler(sample_rate=0.5)
    sampled = sum(1 for i in range(1000) if rs.should_sample(f"req-{i}"))
    assert 350 < sampled < 650

def test_capture():
    rs = RequestSampler()
    rs.capture({"method": "GET", "path": "/api"})
    rs.capture({"method": "POST", "path": "/api"})
    assert len(rs.recent()) == 2
    assert rs.stats()["captured"] == 2
