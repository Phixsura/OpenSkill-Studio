from app.services.app_marketplace_app_app_app_app_app_app_app_launch_checklist import evaluate_checklist

def test_ready():
    required = ["listing", "screenshots", "privacy", "security_scan", "test_install", "docs", "support"]
    r = evaluate_checklist(required)
    assert r["ready_to_launch"]
    assert len(r["missing_required"]) == 0

def test_not_ready():
    r = evaluate_checklist(["listing", "screenshots"])
    assert not r["ready_to_launch"]
    assert len(r["missing_required"]) > 0
    assert r["progress_pct"] == 20
