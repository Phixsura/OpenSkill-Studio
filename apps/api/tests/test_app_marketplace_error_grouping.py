from app.services.app_marketplace_error_grouping import compute_error_fingerprint, group_errors, prioritize_error_groups

def test_fingerprint_stable():
    fp1 = compute_error_fingerprint(error_type="TypeError", message="x is undefined")
    fp2 = compute_error_fingerprint(error_type="TypeError", message="x is undefined")
    assert fp1 == fp2

def test_fingerprint_different():
    fp1 = compute_error_fingerprint(error_type="TypeError", message="x")
    fp2 = compute_error_fingerprint(error_type="RangeError", message="y")
    assert fp1 != fp2

def test_group():
    errors = [{"type": "TypeError", "message": "x is undefined", "timestamp": "2026-01-01"},
              {"type": "TypeError", "message": "x is undefined", "timestamp": "2026-01-02"},
              {"type": "RangeError", "message": "out of range", "timestamp": "2026-01-01"}]
    g = group_errors(errors=errors)
    assert len(g) == 2
    assert g[0]["count"] == 2  # TypeError grouped

def test_prioritize():
    groups = [{"count": 5, "type": "Warning"}, {"count": 3, "type": "TypeError"}]
    r = prioritize_error_groups(groups=groups)
    assert r[0]["type"] == "TypeError"  # critical type boosted
