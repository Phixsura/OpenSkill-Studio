from app.services.app_marketplace_integration_test_harness import create_test_plan, execute_scenario, generate_test_report

def test_plan():
    p = create_test_plan(app_id="a1", scenarios=[{"name": "s1"}, {"name": "s2"}])
    assert p["total"] == 2

def test_scenario_pass():
    r = execute_scenario(scenario={"name": "auth", "steps": [
        {"name": "login", "mock_result": True}, {"name": "token", "mock_result": True}]})
    assert r["passed"]

def test_scenario_fail():
    r = execute_scenario(scenario={"name": "auth", "steps": [
        {"name": "login", "mock_result": True}, {"name": "token", "mock_result": False}]})
    assert not r["passed"]

def test_report():
    plan = {"app_id": "a1"}
    results = [{"passed": True}, {"passed": False}, {"passed": True}]
    r = generate_test_report(plan=plan, results=results)
    assert r["pass_rate"] > 60
    assert r["failed"] == 1
