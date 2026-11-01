from app.services.app_marketplace_app_developer_app_testing_framework import create_test_fixture, run_assertion, build_test_report

def test_fixture():
    f = create_test_fixture(name="user_setup", setup_data={"user_id": "u1"})
    assert f["status"] == "ready"

def test_assert_eq():
    r = run_assertion(actual=42, expected=42, operator="eq")
    assert r["passed"]

def test_assert_fail():
    r = run_assertion(actual=42, expected=99, operator="eq")
    assert not r["passed"]

def test_assert_contains():
    r = run_assertion(actual="hello world", expected="world", operator="contains")
    assert r["passed"]

def test_report_green():
    results = [{"passed": True}, {"passed": True}]
    r = build_test_report(suite_name="unit", results=results)
    assert r["status"] == "green"
    assert r["pass_rate"] == 100

def test_report_red():
    results = [{"passed": True}, {"passed": False}]
    r = build_test_report(suite_name="integration", results=results)
    assert r["status"] == "red"
