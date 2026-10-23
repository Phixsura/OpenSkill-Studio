from app.services.app_marketplace_app_app_app_app_app_app_app_req_dedup import (
    fingerprint_request, is_duplicate, dedup_stats, clear_seen,
)

def test_dedup():
    clear_seen()
    fp = fingerprint_request("POST", "/api/order", '{"item":"x"}', "u1")
    assert len(fp) == 16
    r1 = is_duplicate(fp, window_sec=5)
    assert not r1["duplicate"]
    r2 = is_duplicate(fp, window_sec=5)
    assert r2["duplicate"]
    clear_seen()

def test_different():
    clear_seen()
    fp1 = fingerprint_request("POST", "/a")
    fp2 = fingerprint_request("POST", "/b")
    is_duplicate(fp1)
    assert not is_duplicate(fp2)["duplicate"]
    clear_seen()
