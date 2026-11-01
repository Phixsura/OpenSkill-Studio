from app.services.app_marketplace_app_app_app_app_app_app_app_pipeline_stage import run_pipeline

def test_success():
    r = run_pipeline([
        {"name": "extract", "fn": lambda: {"rows": 100}},
        {"name": "transform", "fn": lambda: {"rows": 95}},
        {"name": "load", "fn": lambda: {"rows": 95}},
    ])
    assert r["passed"] == 3
    assert not r["failed"]

def test_failure_skips():
    r = run_pipeline([
        {"name": "extract", "fn": lambda: {"ok": True}},
        {"name": "transform", "fn": lambda: (_ for _ in ()).throw(ValueError("bad data"))},
        {"name": "load", "fn": lambda: {"ok": True}},
    ])
    assert r["failed"]
    assert r["stages"][1]["status"] == "failed"
    assert r["stages"][2]["status"] == "skipped"
