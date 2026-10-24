from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_log import (
    start_deploy, append_log, get_logs, clear_logs,
)

def test_log_stream():
    clear_logs()
    start_deploy("d1")
    append_log("d1", "info", "Building image...")
    append_log("d1", "info", "Pushing to registry...")
    append_log("d1", "error", "Health check failed")
    r = get_logs("d1")
    assert r["total"] == 3
    assert r["error_count"] == 1
    r2 = get_logs("d1", since_seq=2)
    assert r2["new_count"] == 1
    clear_logs()

def test_escape():
    clear_logs()
    start_deploy("d2")
    append_log("d2", "info", "<script>alert(1)</script>")
    r = get_logs("d2")
    assert "<script>" not in r["logs"][0]["message"]
    clear_logs()
