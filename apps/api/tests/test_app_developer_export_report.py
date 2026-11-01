from app.services.app_developer_export_report import build_export_report, estimate_export_size

def test_build():
    r = build_export_report(developer={"name": "Dev", "_internal": "x"}, apps=[{"id": "a1", "_secret": "y"}], stats={"total": 1})
    assert r["app_count"] == 1
    assert "_internal" not in r["developer"]
    assert "_secret" not in r["apps"][0]

def test_estimate():
    e = estimate_export_size(50)
    assert e["estimated_kb"] > 0
    assert e["estimated_mb"] > 0

def test_estimate_zero():
    e = estimate_export_size(0)
    assert e["estimated_kb"] == 5
