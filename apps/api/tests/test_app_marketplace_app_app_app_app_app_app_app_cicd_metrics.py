from app.services.app_marketplace_app_app_app_app_app_app_app_cicd_metrics import analyze_pipelines, deployment_frequency

def test_analyze():
    runs = [
        {"status": "success", "duration_sec": 120},
        {"status": "success", "duration_sec": 150},
        {"status": "failed", "duration_sec": 200},
    ]
    r = analyze_pipelines(runs)
    assert r["pass_rate"] == 67
    assert r["avg_duration_sec"] == 157
    assert r["fastest_sec"] == 120

def test_frequency():
    deploys = [{"id": i} for i in range(60)]
    r = deployment_frequency(deploys, 30)
    assert r["per_day"] == 2.0
    assert r["dora_level"] == "elite"
