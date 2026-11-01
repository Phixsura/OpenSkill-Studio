from app.services.app_marketplace_app_canary_release import create_canary_release, advance_canary

def test_create():
    r = create_canary_release(app_id="a1", baseline_version="1.0", canary_version="1.1", initial_pct=10)
    assert r["canary"]["traffic_pct"] == 10
    assert r["baseline"]["traffic_pct"] == 90

def test_invalid_pct():
    r = create_canary_release(app_id="a1", baseline_version="1.0", canary_version="1.1", initial_pct=80)
    assert "error" in r

def test_advance():
    rel = create_canary_release(app_id="a1", baseline_version="1.0", canary_version="1.1", initial_pct=10)
    r = advance_canary(release=rel, new_pct=50)
    assert r["canary"]["traffic_pct"] == 50
    assert r["baseline"]["traffic_pct"] == 50

def test_promote():
    rel = create_canary_release(app_id="a1", baseline_version="1.0", canary_version="1.1", initial_pct=10)
    r = advance_canary(release=rel, new_pct=100)
    assert r["status"] == "promoted"
