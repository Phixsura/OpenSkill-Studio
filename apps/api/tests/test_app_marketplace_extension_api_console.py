from app.services.app_marketplace_extension_api_console import DeveloperApiConsoleService


def test_create_env():
    svc = DeveloperApiConsoleService()
    env = svc.create_env("u1", "Production", {"base_url": "https://api.example.com"})
    assert env.name == "Production"
    assert env.is_active is True


def test_interpolate():
    svc = DeveloperApiConsoleService()
    svc.create_env("u1", "Prod", {"host": "api.example.com", "token": "abc123"})
    result = svc.interpolate("u1", "https://{{host}}/v1?token={{token}}")
    assert result == "https://api.example.com/v1?token=abc123"


def test_execute():
    svc = DeveloperApiConsoleService()
    svc.create_env("u1", "Dev", {"host": "localhost:3000"})
    req = svc.execute("u1", "GET", "http://{{host}}/api/users")
    assert req.url == "http://localhost:3000/api/users"
    assert req.response_status == 200


def test_multiple_envs():
    svc = DeveloperApiConsoleService()
    svc.create_env("u1", "Dev", {"host": "localhost"})
    prod = svc.create_env("u1", "Prod", {"host": "api.prod.com"})
    svc.set_active_env("u1", prod.env_id)
    assert svc.interpolate("u1", "{{host}}") == "api.prod.com"


def test_set_variable():
    svc = DeveloperApiConsoleService()
    svc.create_env("u1", "Test", {})
    svc.set_variable("u1", "api_key", "secret123")
    assert svc.interpolate("u1", "Bearer {{api_key}}") == "Bearer secret123"


def test_history():
    svc = DeveloperApiConsoleService()
    svc.create_env("u1", "Dev", {})
    svc.execute("u1", "GET", "/api/a")
    svc.execute("u1", "POST", "/api/b")
    assert len(svc.get_history("u1")) == 2
