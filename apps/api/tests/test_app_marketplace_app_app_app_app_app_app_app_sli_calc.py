from app.services.app_marketplace_app_app_app_app_app_app_app_sli_calc import compute_sli, compute_composite_sli

def test_sli():
    r = compute_sli(metric="availability", good_events=99950, total_events=100000, slo_target=99.9)
    assert r["sli"] == 99.95
    assert r["met"]
    assert r["status"] == "met"
    assert r["bad_events"] == 50

def test_breached():
    r = compute_sli(metric="latency", good_events=99000, total_events=100000, slo_target=99.9)
    assert r["sli"] == 99.0
    assert not r["met"]

def test_composite():
    slis = [
        compute_sli(metric="avail", good_events=99950, total_events=100000),
        compute_sli(metric="latency", good_events=99000, total_events=100000),
    ]
    c = compute_composite_sli(slis)
    assert not c["all_met"]
    assert "latency" in c["breached_metrics"]
