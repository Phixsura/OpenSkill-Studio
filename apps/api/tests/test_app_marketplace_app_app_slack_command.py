from app.services.app_marketplace_app_app_slack_command import parse_command, verify_slack_signature, list_commands

def test_parse_status():
    r = parse_command(text="/status myapp")
    assert r["valid"]
    assert r["command"] == "/status"
    assert r["args"] == ["myapp"]

def test_unknown():
    r = parse_command(text="/unknown")
    assert "error" in r

def test_verify():
    secret = "test_secret"
    body = "token=abc&command=/status"
    ts = "1234567890"
    base = f"v0:{ts}:{body}"
    sig = "v0=" + hmac.new(secret.encode(), base.encode(), hashlib.sha256).hexdigest()
    assert verify_slack_signature(body=body, timestamp=ts, signature=sig, signing_secret=secret)

def test_list():
    cmds = list_commands()
    assert len(cmds) == 5
    assert any(c["command"] == "/deploy" for c in cmds)

import hmac, hashlib
