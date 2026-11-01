from app.services.app_marketplace_extension_env_config import ExtEnvConfigService

def test_set_and_get():
    svc = ExtEnvConfigService()
    svc.set("ext-1", "development", "API_URL", "http://localhost:8000")
    assert svc.get("ext-1", "development")["API_URL"] == "http://localhost:8000"

def test_promote():
    svc = ExtEnvConfigService()
    svc.set("ext-1", "development", "DB_HOST", "localhost")
    svc.set("ext-1", "development", "DEBUG", "true")
    svc.promote("ext-1", "development", "staging")
    assert svc.get("ext-1", "staging")["DB_HOST"] == "localhost"

def test_lock():
    svc = ExtEnvConfigService()
    svc.set("ext-1", "production", "KEY", "val")
    svc.lock("ext-1", "production")
    assert svc.set("ext-1", "production", "KEY", "new") is False

def test_diff():
    svc = ExtEnvConfigService()
    svc.set("ext-1", "development", "A", "1")
    svc.set("ext-1", "development", "B", "2")
    svc.set("ext-1", "staging", "A", "1")
    svc.set("ext-1", "staging", "B", "3")
    d = svc.diff("ext-1", "development", "staging")
    assert "B" in d
    assert "A" not in d
