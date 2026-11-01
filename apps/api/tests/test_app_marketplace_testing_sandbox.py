from app.services.app_marketplace_testing_sandbox import create_test_environment, run_test_suite, teardown_sandbox

def test_create():
    env = create_test_environment(app_id="a1", version_id="v1", developer_id="d1")
    assert env["status"] == "provisioning"
    assert "sandbox" in env["endpoints"]["api"]

def test_with_config():
    env = create_test_environment(app_id="a1", version_id="v1", developer_id="d1", config_overrides={"debug": True})
    assert env["config"]["debug"]

def test_run_all_pass():
    r = run_test_suite(sandbox_id="s1", tests=[
        {"name": "health", "expected_status": 200, "actual_status": 200},
        {"name": "auth", "expected_status": 200, "actual_status": 200}])
    assert r["pass_rate"] == 100

def test_run_with_failure():
    r = run_test_suite(sandbox_id="s1", tests=[
        {"name": "ok", "expected_status": 200, "actual_status": 200},
        {"name": "fail", "expected_status": 200, "actual_status": 500}])
    assert r["failed"] == 1

def test_teardown():
    r = teardown_sandbox(sandbox_id="s1")
    assert r["status"] == "destroyed"
