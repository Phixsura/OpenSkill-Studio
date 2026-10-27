from app.services.app_marketplace_extension_config_validator import ExtConfigValidatorService

def test_valid_config():
    svc = ExtConfigValidatorService()
    config = {"name": "my-extension", "version": "1.0.0", "description": "A great extension",
              "author": "dev@example.com", "entry_point": "src/index.js"}
    ok, issues = svc.validate(config)
    assert ok is True

def test_missing_fields():
    svc = ExtConfigValidatorService()
    ok, issues = svc.validate({"name": "test"})
    assert ok is False
    assert any("Missing required" in i for i in issues)

def test_invalid_version():
    svc = ExtConfigValidatorService()
    config = {"name": "my-ext", "version": "not-semver", "description": "Desc here long",
              "author": "dev", "entry_point": "index.js"}
    ok, issues = svc.validate(config)
    assert ok is False
    assert any("Invalid version" in i for i in issues)

def test_template():
    svc = ExtConfigValidatorService()
    t = svc.generate_template("my-ext", "dev@example.com")
    assert t["name"] == "my-ext"
    assert t["version"] == "0.1.0"
