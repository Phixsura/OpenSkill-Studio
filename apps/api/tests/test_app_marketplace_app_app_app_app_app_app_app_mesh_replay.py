from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_replay import MeshTrafficReplay

def test_capture_replay():
    mtr = MeshTrafficReplay()
    mtr.capture("web", "api", "GET", "/users", 200, 15)
    mtr.capture("api", "db", "SELECT", "users", 200, 5)
    mtr.capture("web", "api", "POST", "/orders", 201, 30)
    r = mtr.replay(source_filter="web")
    assert r["replayed"] == 2
    assert mtr.stats()["replayed"] == 2

def test_range():
    mtr = MeshTrafficReplay()
    for i in range(5):
        mtr.capture("a", "b", "GET", f"/{i}", 200, 10)
    r = mtr.replay(from_seq=2, to_seq=4)
    assert r["replayed"] == 3
