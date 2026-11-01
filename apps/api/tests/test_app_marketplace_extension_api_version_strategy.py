from app.services.app_marketplace_extension_api_version_strategy import ApiVersionStrategyService


def test_path_negotiation():
    svc = ApiVersionStrategyService()
    svc.register_version("v1")
    svc.register_version("v2")
    result = svc.negotiate(path="/v2/users")
    assert result["version"] == "v2"
    assert result["source"] == "path"


def test_header_negotiation():
    svc = ApiVersionStrategyService()
    svc.register_version("v3")
    result = svc.negotiate(accept_header="application/vnd.myapi.v3+json")
    assert result["version"] == "v3"
    assert result["source"] == "header"


def test_query_negotiation():
    svc = ApiVersionStrategyService()
    svc.register_version("v2")
    result = svc.negotiate(query_version="v2")
    assert result["version"] == "v2"
    assert result["source"] == "query"


def test_default_version():
    svc = ApiVersionStrategyService(default_version="v1")
    svc.register_version("v1")
    result = svc.negotiate()
    assert result["version"] == "v1"
    assert result["source"] == "default"


def test_path_takes_priority():
    svc = ApiVersionStrategyService()
    svc.register_version("v1")
    svc.register_version("v2")
    result = svc.negotiate(path="/v1/data", query_version="v2")
    assert result["version"] == "v1"  # path wins


def test_deprecated_warning():
    svc = ApiVersionStrategyService()
    svc.register_version("v1")
    svc.deprecate("v1")
    result = svc.negotiate(path="/v1/users")
    assert result["status"] == "deprecated"
    assert "warning" in result


def test_sunset_error():
    svc = ApiVersionStrategyService()
    svc.register_version("v1")
    svc.sunset("v1")
    result = svc.negotiate(path="/v1/users")
    assert result["status"] == "sunset"
    assert "error" in result


def test_route_handler():
    svc = ApiVersionStrategyService()
    svc.register_version("v1")
    svc.register_version("v2")
    svc.register_handler("v1", "/users", lambda: "v1_users")
    svc.register_handler("v2", "/users", lambda: "v2_users")
    h1 = svc.route("v1", "/users")
    h2 = svc.route("v2", "/users")
    assert h1() == "v1_users"
    assert h2() == "v2_users"


def test_sunset_blocks_routing():
    svc = ApiVersionStrategyService()
    svc.register_version("v1")
    svc.register_handler("v1", "/data", lambda: "data")
    svc.sunset("v1")
    assert svc.route("v1", "/data") is None


def test_migration_guide():
    svc = ApiVersionStrategyService()
    svc.add_migration_guide("v1", "v2", "Replace /users with /accounts")
    assert "accounts" in svc.get_migration_guide("v1", "v2")
