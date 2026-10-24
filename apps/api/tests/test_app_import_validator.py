from app.services.app_import_validator import validate_import_structure

def test_valid():
    assert validate_import_structure({"export_version": "1.0", "app": {"name": "X", "slug": "x"}}) == []

def test_missing_version():
    assert len(validate_import_structure({"app": {"name": "X", "slug": "x"}})) > 0

def test_missing_app():
    assert len(validate_import_structure({"export_version": "1.0"})) > 0

def test_missing_name():
    assert len(validate_import_structure({"export_version": "1.0", "app": {"slug": "x"}})) > 0
