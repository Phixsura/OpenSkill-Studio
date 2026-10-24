from app.services.app_marketplace_app_app_app_app_app_app_app_req_replay import RequestReplayEngine

def test_capture_replay():
    rre = RequestReplayEngine()
    rre.capture("GET", "/api/users", status=200)
    rre.capture("POST", "/api/orders", body='{"item":"x"}', status=201)
    rre.capture("GET", "/api/users/1", status=200)
    r = rre.replay(filter_path="/api/users")
    assert r["replayed"] == 2

def test_range():
    rre = RequestReplayEngine()
    for i in range(10):
        rre.capture("GET", f"/path/{i}")
    r = rre.replay(from_seq=5, to_seq=8)
    assert r["replayed"] == 4
    assert rre.stats()["replayed"] == 4
