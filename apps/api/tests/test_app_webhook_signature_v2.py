import time
from app.services.app_webhook_signature_v2 import sign_v2, verify_v2

def test_sign_verify():
    result = sign_v2(payload=b'{"test":true}', secret="mysecret")
    v = verify_v2(payload=b'{"test":true}', signature=result["signature"], timestamp=result["timestamp"], secret="mysecret")
    assert v["valid"] is True

def test_wrong_secret():
    result = sign_v2(payload=b'test', secret="key1")
    v = verify_v2(payload=b'test', signature=result["signature"], timestamp=result["timestamp"], secret="key2")
    assert v["valid"] is False

def test_tampered_payload():
    result = sign_v2(payload=b'original', secret="key")
    v = verify_v2(payload=b'tampered', signature=result["signature"], timestamp=result["timestamp"], secret="key")
    assert v["valid"] is False

def test_expired_timestamp():
    old_ts = int(time.time()) - 600
    result = sign_v2(payload=b'test', secret="key", timestamp=old_ts)
    v = verify_v2(payload=b'test', signature=result["signature"], timestamp=old_ts, secret="key")
    assert v["valid"] is False
    assert v["reason"] == "timestamp_expired"

def test_signature_format():
    result = sign_v2(payload=b'x', secret="s")
    assert result["signature"].startswith("v2=")

def test_timestamp_included():
    result = sign_v2(payload=b'x', secret="s")
    assert isinstance(result["timestamp"], int)
