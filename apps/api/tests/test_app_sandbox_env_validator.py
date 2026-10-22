from app.services.app_sandbox_env_validator import validate_env_var, validate_env_map

def test_valid():
    assert validate_env_var("API_KEY", "secret123") == []

def test_bad_key():
    assert len(validate_env_var("lowercase", "val")) > 0

def test_forbidden_prefix():
    assert len(validate_env_var("PATH_OVERRIDE", "x")) > 0
    assert len(validate_env_var("LD_PRELOAD", "/evil.so")) > 0

def test_bad_value():
    assert len(validate_env_var("KEY", "val\x00null")) > 0

def test_validate_map_ok():
    assert validate_env_map({"API_KEY": "val", "SECRET": "abc"}) == []

def test_validate_map_errors():
    errors = validate_env_map({"good": "val", "PATH_X": "y"})
    assert len(errors) >= 2
