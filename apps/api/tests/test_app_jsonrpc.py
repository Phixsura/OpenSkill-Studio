"""JSON-RPC protocol tests."""
import json, pytest
from app.services.app_jsonrpc import build_request, build_response, build_error, parse_message

def test_build_request():
    msg = json.loads(build_request("execute", {"fn": "test"}))
    assert msg["jsonrpc"] == "2.0"
    assert msg["method"] == "execute"

def test_build_response():
    msg = json.loads(build_response({"ok": True}))
    assert msg["result"]["ok"] is True

def test_build_error():
    msg = json.loads(build_error(-32600, "Invalid"))
    assert msg["error"]["code"] == -32600

def test_parse_request():
    r = parse_message(build_request("test"))
    assert r["valid"] is True
    assert r["is_request"] is True

def test_parse_response():
    r = parse_message(build_response("ok"))
    assert r["valid"] is True
    assert r["is_response"] is True

def test_parse_invalid_json():
    r = parse_message("not json")
    assert r["valid"] is False

def test_parse_not_jsonrpc():
    r = parse_message('{"version": "1.0"}')
    assert r["valid"] is False
