from app.services.app_marketplace_app_app_app_app_app_app_app_build_status import track_builds, flaky_tests

def test_track():
    r = track_builds([
        {"status": "passed", "duration_sec": 120},
        {"status": "passed", "duration_sec": 150},
        {"status": "failed", "duration_sec": 200},
        {"status": "running"},
    ])
    assert r["passed"] == 2
    assert r["failed"] == 1
    assert r["pass_rate"] == 67
    assert r["health"] == "red"

def test_flaky():
    builds = [
        {"tests": [{"name": "test_login", "passed": True}, {"name": "test_flaky", "passed": True}]},
        {"tests": [{"name": "test_login", "passed": True}, {"name": "test_flaky", "passed": False}]},
        {"tests": [{"name": "test_login", "passed": True}, {"name": "test_flaky", "passed": True}]},
    ]
    r = flaky_tests(builds)
    assert len(r) == 1
    assert r[0]["name"] == "test_flaky"
