from app.services.app_marketplace_app_sandbox_console import create_console_session, execute_command, build_console_history

def test_create():
    s = create_console_session(app_id="a1", developer_id="d1")
    assert s["status"] == "active"
    assert s["language"] == "javascript"

def test_unsupported():
    s = create_console_session(app_id="a1", developer_id="d1", language="ruby")
    assert s["error"]

def test_execute():
    session = {"language": "javascript"}
    r = execute_command(session=session, code="console.log('hello')")
    assert r["output"]
    assert r["error"] is None

def test_too_long():
    session = {"language": "javascript"}
    r = execute_command(session=session, code="x" * 20000)
    assert r["error"]

def test_history():
    commands = [{"input": "1+1", "output": "2"}, {"input": "a=5", "output": "5"}]
    h = build_console_history(commands=commands)
    assert len(h) == 2
    assert h[0]["index"] == 0
