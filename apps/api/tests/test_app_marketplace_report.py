from app.services.app_marketplace_report import generate_monthly_report

def test_report():
    r = generate_monthly_report(month="2026-10", new_apps=15, new_developers=5, total_installs=500,
        top_apps=[{"name": "App1", "installs": 100}], avg_health=96)
    assert r["health_grade"] == "A"
    assert r["new_apps"] == 15

def test_grade_b():
    r = generate_monthly_report(month="2026-10", new_apps=0, new_developers=0, total_installs=0, top_apps=[], avg_health=88)
    assert r["health_grade"] == "B"

def test_top_apps_limit():
    top = [{"name": f"a{i}"} for i in range(10)]
    r = generate_monthly_report(month="x", new_apps=0, new_developers=0, total_installs=0, top_apps=top, avg_health=100)
    assert len(r["top_apps"]) == 5
