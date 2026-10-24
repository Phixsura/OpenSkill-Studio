from app.services.app_marketplace_app_app_command_result import format_command_result

def test_success():
    r = format_command_result(command="npm test", exit_code=0,
        stdout="All tests passed\n5 tests, 0 failures", stderr="", duration_ms=3200)
    assert r["success"]
    assert r["output_line_count"] == 2
    assert r["duration_formatted"] == "3.2s"

def test_failure():
    r = format_command_result(command="npm build", exit_code=1,
        stdout="", stderr="Error: Module not found", duration_ms=500)
    assert not r["success"]
    assert r["error_line_count"] == 1
    assert r["duration_formatted"] == "500ms"
