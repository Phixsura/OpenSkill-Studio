from app.services.app_manifest_schema_validator import validate_schema_structure

def test_valid():
    m = {"schema_version": "1.0", "app": {"name": "X", "slug": "x", "version": "1.0.0", "category": "connector"}}
    assert validate_schema_structure(m) == []

def test_missing_schema_version():
    assert len(validate_schema_structure({"app": {"name": "X", "slug": "x", "version": "1.0", "category": "c"}})) > 0

def test_missing_app():
    assert len(validate_schema_structure({"schema_version": "1.0"})) > 0

def test_missing_app_name():
    m = {"schema_version": "1.0", "app": {"slug": "x", "version": "1.0", "category": "c"}}
    assert any("app.name" in e for e in validate_schema_structure(m))

def test_not_dict():
    assert len(validate_schema_structure("string")) > 0

def test_wrong_type():
    m = {"schema_version": 1.0, "app": {"name": "X", "slug": "x", "version": "1.0", "category": "c"}}
    assert len(validate_schema_structure(m)) > 0
