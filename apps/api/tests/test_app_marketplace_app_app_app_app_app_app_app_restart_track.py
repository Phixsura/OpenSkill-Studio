from app.services.app_marketplace_app_app_app_app_app_app_app_restart_track import RestartTracker

def test_track():
    rt = RestartTracker(crash_loop_threshold=3)
    rt.record_restart("api", "OOM", 137)
    rt.record_restart("api", "OOM", 137)
    r = rt.record_restart("api", "OOM", 137)
    assert r["crash_loop"]
    assert r["restart_count"] == 3

def test_crash_loops():
    rt = RestartTracker(crash_loop_threshold=2)
    rt.record_restart("api", "OOM", 137)
    rt.record_restart("api", "OOM", 137)
    rt.record_restart("worker", "signal", 0)
    loops = rt.crash_loops()
    assert len(loops) == 1
    assert loops[0]["service"] == "api"
    assert rt.stats()["total_restarts"] == 3
