from app.services.app_marketplace_extension_api_compat_checker import (
    ApiCompatCheckerService, ApiEndpoint
)


def test_identical_apis():
    cc = ApiCompatCheckerService()
    api = [ApiEndpoint("/users", "GET", response_fields=["id", "name"])]
    result = cc.check(api, api)
    assert result["compatible"] is True
    assert result["breaking_count"] == 0


def test_removed_endpoint():
    cc = ApiCompatCheckerService()
    old = [ApiEndpoint("/users", "GET"), ApiEndpoint("/users", "DELETE")]
    new = [ApiEndpoint("/users", "GET")]
    result = cc.check(old, new)
    assert result["compatible"] is False
    assert any("removed" in i["message"].lower() for i in result["issues"])


def test_added_endpoint():
    cc = ApiCompatCheckerService()
    old = [ApiEndpoint("/users", "GET")]
    new = [ApiEndpoint("/users", "GET"), ApiEndpoint("/users", "POST")]
    result = cc.check(old, new)
    assert result["compatible"] is True  # adding is non-breaking


def test_new_required_param():
    cc = ApiCompatCheckerService()
    old = [ApiEndpoint("/users", "GET")]
    new = [ApiEndpoint("/users", "GET",
                       params={"api_key": {"type": "string", "required": True}})]
    result = cc.check(old, new)
    assert result["compatible"] is False
    assert any("required parameter" in i["message"].lower() for i in result["issues"])


def test_new_optional_param():
    cc = ApiCompatCheckerService()
    old = [ApiEndpoint("/users", "GET")]
    new = [ApiEndpoint("/users", "GET",
                       params={"page": {"type": "integer", "required": False}})]
    result = cc.check(old, new)
    assert result["compatible"] is True


def test_response_field_removed():
    cc = ApiCompatCheckerService()
    old = [ApiEndpoint("/users", "GET", response_fields=["id", "name", "email"])]
    new = [ApiEndpoint("/users", "GET", response_fields=["id", "name"])]
    result = cc.check(old, new)
    assert result["compatible"] is False
    assert any("email" in i["message"] for i in result["issues"])


def test_param_type_change():
    cc = ApiCompatCheckerService()
    old = [ApiEndpoint("/users", "GET",
                       params={"id": {"type": "integer"}})]
    new = [ApiEndpoint("/users", "GET",
                       params={"id": {"type": "string"}})]
    result = cc.check(old, new)
    assert result["compatible"] is False


def test_deprecation():
    cc = ApiCompatCheckerService()
    old = [ApiEndpoint("/old", "GET")]
    new = [ApiEndpoint("/old", "GET", deprecated=True)]
    result = cc.check(old, new)
    assert result["compatible"] is True  # deprecation is warning, not breaking
    assert result["warning_count"] >= 1


def test_score():
    cc = ApiCompatCheckerService()
    old = [ApiEndpoint(f"/ep{i}", "GET") for i in range(10)]
    new = [ApiEndpoint(f"/ep{i}", "GET") for i in range(8)]  # 2 removed
    result = cc.check(old, new)
    assert result["score"] < 100


def test_optional_to_required():
    cc = ApiCompatCheckerService()
    old = [ApiEndpoint("/data", "POST",
                       params={"filter": {"type": "string", "required": False}})]
    new = [ApiEndpoint("/data", "POST",
                       params={"filter": {"type": "string", "required": True}})]
    result = cc.check(old, new)
    assert result["compatible"] is False
    assert any("became required" in i["message"] for i in result["issues"])
