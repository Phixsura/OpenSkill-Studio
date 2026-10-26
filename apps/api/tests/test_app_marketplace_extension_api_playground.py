from app.services.app_marketplace_extension_api_playground import (
    ApiPlaygroundService, PlaygroundRequest,
)


def test_execute_get():
    svc = ApiPlaygroundService()
    req = PlaygroundRequest(method="GET", path="/api/v1/health")
    result = svc.execute(req)
    assert result.response.status_code == 200
    assert "ok" in result.response.body


def test_execute_with_assertions():
    svc = ApiPlaygroundService()
    req = PlaygroundRequest(method="GET", path="/api/v1/health")
    assertions = [
        {"check": "status", "expected": 200},
        {"check": "body_contains", "expected": "ok"},
    ]
    result = svc.execute(req, assertions)
    assert result.assertions_passed == 2
    assert result.assertions_failed == 0


def test_failed_assertion():
    svc = ApiPlaygroundService()
    req = PlaygroundRequest(method="GET", path="/api/v1/health")
    result = svc.execute(req, [{"check": "status", "expected": 404}])
    assert result.assertions_failed == 1


def test_variable_interpolation():
    svc = ApiPlaygroundService()
    svc.set_variable("ext_id", "ext-123")
    req = PlaygroundRequest(method="GET", path="/api/v1/extensions/{{ext_id}}")
    result = svc.execute(req)
    assert result.request.path == "/api/v1/extensions/ext-123"
    assert result.response.status_code == 200


def test_custom_mock():
    svc = ApiPlaygroundService()
    svc.set_mock("POST", "/api/v1/custom", 201, {"created": True})
    req = PlaygroundRequest(method="POST", path="/api/v1/custom")
    result = svc.execute(req)
    assert result.response.status_code == 201
    assert "created" in result.response.body


def test_history():
    svc = ApiPlaygroundService()
    svc.execute(PlaygroundRequest(method="GET", path="/api/v1/health"))
    svc.execute(PlaygroundRequest(method="GET", path="/api/v1/health"))
    assert len(svc.get_history()) == 2
    assert svc.clear_history() == 2


def test_not_found():
    svc = ApiPlaygroundService()
    req = PlaygroundRequest(method="GET", path="/unknown")
    result = svc.execute(req)
    assert result.response.status_code == 404
