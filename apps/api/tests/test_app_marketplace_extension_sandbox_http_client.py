from app.services.app_marketplace_extension_sandbox_http_client import (
    SandboxHttpClientService,
)


def test_basic_request():
    svc = SandboxHttpClientService()
    log = svc.request("sb-1", "GET", "https://api.example.com/data")
    assert not log.blocked
    assert log.response.status_code == 200


def test_block_private_ip():
    svc = SandboxHttpClientService()
    log = svc.request("sb-1", "GET", "http://127.0.0.1/admin")
    assert log.blocked is True
    assert "Private" in log.block_reason


def test_block_metadata():
    svc = SandboxHttpClientService()
    log = svc.request("sb-1", "GET", "http://169.254.169.254/latest/meta-data")
    assert log.blocked is True


def test_allowlist():
    svc = SandboxHttpClientService()
    svc.set_allowlist("sb-1", ["https://api.example.com/*"])
    log1 = svc.request("sb-1", "GET", "https://api.example.com/data")
    assert not log1.blocked
    log2 = svc.request("sb-1", "GET", "https://evil.com/steal")
    assert log2.blocked
    assert "allowlist" in log2.block_reason


def test_header_sanitization():
    svc = SandboxHttpClientService()
    log = svc.request("sb-1", "GET", "https://api.example.com",
                      headers={"Authorization": "Bearer secret", "Accept": "application/json"})
    assert "Authorization" not in log.request.headers
    assert "Accept" in log.request.headers


def test_body_size_limit():
    svc = SandboxHttpClientService()
    big_body = "x" * (6 * 1024 * 1024)
    log = svc.request("sb-1", "POST", "https://api.example.com", body=big_body)
    assert log.blocked is True
    assert "too large" in log.block_reason


def test_invalid_scheme():
    svc = SandboxHttpClientService()
    log = svc.request("sb-1", "GET", "ftp://files.example.com/data")
    assert log.blocked is True
    assert "scheme" in log.block_reason


def test_request_log():
    svc = SandboxHttpClientService()
    svc.request("sb-1", "GET", "https://api.example.com")
    svc.request("sb-1", "GET", "http://127.0.0.1")
    assert len(svc.get_log()) == 2
    assert svc.get_blocked_count() == 1
