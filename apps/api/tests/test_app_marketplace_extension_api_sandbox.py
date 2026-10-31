from app.services.app_marketplace_extension_api_sandbox import ExtApiSandboxService

def test_execute():
    svc = ExtApiSandboxService()
    req = svc.execute("dev-1", "GET", "/api/users")
    assert req.response_code == 200
    assert req.method == "GET"

def test_mock_response():
    svc = ExtApiSandboxService()
    svc.add_mock("/api/error", "POST", 500, '{"error":"fail"}')
    req = svc.execute("dev-1", "POST", "/api/error")
    assert req.response_code == 500

def test_history():
    svc = ExtApiSandboxService()
    svc.execute("dev-1", "GET", "/a")
    svc.execute("dev-1", "POST", "/b")
    assert len(svc.get_history("dev-1")) == 2

def test_invalid_method():
    svc = ExtApiSandboxService()
    try:
        svc.execute("dev-1", "INVALID", "/api")
        assert False
    except ValueError:
        pass
