from app.services.app_sandbox_output_parser import parse_sandbox_output, extract_logs

def test_parse_success():
    r = parse_sandbox_output('{"jsonrpc":"2.0","result":{"ok":true},"id":1}')
    assert r["success"] is True
    assert r["output"]["ok"] is True

def test_parse_error():
    r = parse_sandbox_output('{"jsonrpc":"2.0","error":{"code":-1,"message":"fail"},"id":1}')
    assert r["success"] is False
    assert "fail" in r["error"]

def test_parse_with_logs():
    stdout = "Starting...\nProcessing...\n{\"result\":{\"done\":true}}"
    r = parse_sandbox_output(stdout)
    assert r["success"] is True

def test_parse_no_json():
    r = parse_sandbox_output("just plain text\nno json here")
    assert r["success"] is False

def test_extract_logs():
    stdout = "Log line 1\n{\"result\":{}}\nLog line 2"
    logs = extract_logs(stdout)
    assert len(logs) == 2
    assert logs[0]["message"] == "Log line 1"

def test_extract_empty():
    assert extract_logs("") == []
