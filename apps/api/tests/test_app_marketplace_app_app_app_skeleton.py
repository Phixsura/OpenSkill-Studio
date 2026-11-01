from app.services.app_marketplace_app_app_app_skeleton import generate_skeleton

def test_basic():
    r = generate_skeleton(app_name="my-app", runtime="node")
    assert r["file_count"] >= 4
    assert any(f["path"] == "package.json" for f in r["files"])

def test_python():
    r = generate_skeleton(app_name="pyapp", runtime="python")
    assert any(f["path"] == "pyproject.toml" for f in r["files"])
    assert any("main.py" in f["path"] for f in r["files"])

def test_features():
    r = generate_skeleton(app_name="full", runtime="node", features=["tests", "docker", "ci"])
    assert any("Dockerfile" in f["path"] for f in r["files"])
    assert any("ci.yml" in f["path"] for f in r["files"])
    assert any("test" in f["path"] for f in r["files"])
