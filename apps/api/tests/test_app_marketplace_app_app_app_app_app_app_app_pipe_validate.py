from app.services.app_marketplace_app_app_app_app_app_app_app_pipe_validate import validate_pipeline, pipeline_summary

def test_valid():
    r = validate_pipeline({"stages": [
        {"name": "build", "action": "docker_build"},
        {"name": "test", "action": "run_tests"},
        {"name": "deploy", "action": "k8s_deploy"},
    ], "trigger": "push"})
    assert r["valid"]
    assert r["stages"] == 3

def test_invalid():
    r = validate_pipeline({"stages": [
        {"name": "build", "action": "build"},
        {"name": "build", "action": "test"},  # duplicate
    ], "trigger": "invalid"})
    assert not r["valid"]
    assert len(r["errors"]) == 2

def test_summary():
    r = pipeline_summary([
        {"stages": [{"name": "a", "action": "b"}]},
        {"stages": []},
    ])
    assert r["valid"] == 1
    assert r["invalid"] == 1
