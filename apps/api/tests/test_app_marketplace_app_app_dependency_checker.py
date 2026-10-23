from app.services.app_marketplace_app_app_dependency_checker import check_dependencies

def test_check():
    pkgs = [
        {"name": "react", "current": "18.2.0", "latest": "18.3.1"},
        {"name": "next", "current": "14.0.0", "latest": "15.1.0"},
        {"name": "lodash", "current": "4.17.21", "latest": "4.17.21"},
    ]
    r = check_dependencies(packages=pkgs)
    assert r["total"] == 3
    assert r["outdated"] == 2
    assert r["major_updates"] == 1
    assert r["up_to_date"] == 1
    assert r["health"] == "critical"
    assert r["packages"][0]["breaking"]  # major sorted first

def test_all_current():
    r = check_dependencies(packages=[{"name": "a", "current": "1.0.0", "latest": "1.0.0"}])
    assert r["health"] == "good"
    assert r["outdated"] == 0
