from app.services.app_marketplace_app_app_app_app_app_app_app_onboard_check import get_checklist

def test_partial():
    r = get_checklist(["account", "mfa", "ssh_key"])
    assert r["completed"] == 3
    assert r["progress_pct"] == 38
    assert not r["ready_to_contribute"]

def test_ready():
    r = get_checklist(["account", "mfa", "ssh_key", "team_join", "repo_access", "local_env"])
    assert r["required_complete"]
    assert r["ready_to_contribute"]
