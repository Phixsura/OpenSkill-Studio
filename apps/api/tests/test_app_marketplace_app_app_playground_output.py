from app.services.app_marketplace_app_app_playground_output import format_output, detect_language_errors

def test_success():
    r = format_output(stdout="Hello World\n", stderr="", exit_code=0, execution_ms=42)
    assert r["success"]
    assert r["stdout_lines"] == 1
    assert not r["has_error"]

def test_error():
    r = format_output(stdout="", stderr="Error!", exit_code=1, execution_ms=10)
    assert not r["success"]
    assert r["has_error"]

def test_detect_python():
    output = 'File "main.py", line 5\nNameError: name \'x\' is not defined'
    errors = detect_language_errors(output=output, language="python")
    assert len(errors) >= 2

def test_detect_js():
    errors = detect_language_errors(output="TypeError: undefined is not a function", language="javascript")
    assert len(errors) == 1
    assert errors[0]["type"] == "runtime_error"
