from app.services.app_marketplace_app_app_step_indicator import build_step_indicator

def test_middle():
    r = build_step_indicator(steps=["Start", "Config", "Review", "Deploy"], current_step=2)
    assert r["steps"][0]["status"] == "completed"
    assert r["steps"][1]["status"] == "completed"
    assert r["steps"][2]["status"] == "current"
    assert r["steps"][3]["status"] == "upcoming"
    assert r["progress_pct"] == 67

def test_first():
    r = build_step_indicator(steps=["A", "B", "C"], current_step=0)
    assert r["is_first"]
    assert not r["is_last"]

def test_last():
    r = build_step_indicator(steps=["A", "B"], current_step=1)
    assert r["is_last"]
    assert r["progress_pct"] == 100
