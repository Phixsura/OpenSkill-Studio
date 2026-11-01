from app.services.app_sandbox_env_validator import validate_env_var, validate_env_map

def test_valid_openskill():
    assert validate_env_var("OPENSKILL_SECRET_API_KEY", "val") == []

def test_valid_app():
    assert validate_env_var("APP_CONFIG_URL", "https://x.com") == []

def test_reject_generic():
    assert len(validate_env_var("API_KEY", "val")) > 0

def test_reject_path():
    assert len(validate_env_var("PATH", "/evil")) > 0

def test_reject_ld_preload():
    assert len(validate_env_var("LD_PRELOAD", "/evil.so")) > 0

def test_reject_lowercase():
    assert len(validate_env_var("openskill_key", "val")) > 0

def test_bad_value():
    assert len(validate_env_var("OPENSKILL_KEY", "val\x00null")) > 0

def test_map_ok():
    assert validate_env_map({"OPENSKILL_KEY": "val", "APP_URL": "https://x.com"}) == []

def test_map_errors():
    errors = validate_env_map({"PATH": "/x", "APP_OK": "y"})
    assert len(errors) == 1
