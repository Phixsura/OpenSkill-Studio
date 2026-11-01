from app.services.app_sandbox_file_validator import validate_bundle

def test_valid():
    assert validate_bundle({"src/index.js": 1000, "package.json": 200}) == []

def test_too_many_files():
    files = {f"file{i}.js": 100 for i in range(600)}
    assert len(validate_bundle(files)) > 0

def test_too_large():
    assert len(validate_bundle({"big.js": 60_000_000})) > 0

def test_blocked_ext():
    assert len(validate_bundle({"virus.exe": 100})) > 0

def test_path_traversal():
    assert len(validate_bundle({"../../../etc/passwd": 10})) > 0

def test_absolute_path():
    assert len(validate_bundle({"/etc/passwd": 10})) > 0
