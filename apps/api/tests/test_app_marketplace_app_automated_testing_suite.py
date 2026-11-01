from app.services.app_marketplace_app_automated_testing_suite import create_test_suite, run_test_case, run_full_suite

def test_create():
    s = create_test_suite(app_id="a1", name="smoke", test_cases=[{"name": "health"}])
    assert s["case_count"] == 1

def test_empty():
    s = create_test_suite(app_id="a1", name="x", test_cases=[])
    assert s["error"]

def test_pass():
    r = run_test_case(test_case={"name": "health", "expected_status": 200, "mock_status": 200})
    assert r["passed"]

def test_fail():
    r = run_test_case(test_case={"name": "auth", "expected_status": 200, "mock_status": 401})
    assert not r["passed"]

def test_body_check():
    r = run_test_case(test_case={"name": "body", "expected_status": 200, "mock_status": 200,
                                   "expected_body_contains": "ok", "mock_body": "status: ok"})
    assert r["passed"]

def test_suite():
    cases = [{"name": "a", "expected_status": 200, "mock_status": 200},
             {"name": "b", "expected_status": 200, "mock_status": 500}]
    r = run_full_suite(test_cases=cases)
    assert r["passed"] == 1
    assert r["pass_rate"] == 50.0
