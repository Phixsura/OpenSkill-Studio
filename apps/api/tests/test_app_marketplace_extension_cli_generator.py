from app.services.app_marketplace_extension_cli_generator import (
    CLIGeneratorService,
)
import json
import pytest


def test_scaffold_node():
    svc = CLIGeneratorService()
    result = svc.scaffold("my-ext", "node20", description="A test extension")
    assert result.total_files == 6
    paths = {f.path for f in result.files}
    assert "manifest.json" in paths
    assert "src/index.ts" in paths
    assert "package.json" in paths
    assert "README.md" in paths


def test_scaffold_python():
    svc = CLIGeneratorService()
    result = svc.scaffold("my-ext", "python3.12")
    paths = {f.path for f in result.files}
    assert "src/main.py" in paths
    assert "pyproject.toml" in paths
    assert "tests/test_main.py" in paths


def test_manifest_content():
    svc = CLIGeneratorService()
    result = svc.scaffold("cool-ext", "node20")
    manifest_file = next(f for f in result.files if f.path == "manifest.json")
    manifest = json.loads(manifest_file.content)
    assert manifest["name"] == "cool-ext"
    assert manifest["runtime"] == "node20"
    assert manifest["manifest_version"] == "2.0"


def test_invalid_runtime():
    svc = CLIGeneratorService()
    with pytest.raises(ValueError, match="Unsupported"):
        svc.scaffold("ext", "ruby3.2")


def test_invalid_name():
    svc = CLIGeneratorService()
    with pytest.raises(ValueError, match="Invalid"):
        svc.scaffold("bad name!", "node20")


def test_entrypoint_has_activate():
    svc = CLIGeneratorService()
    result = svc.scaffold("test-ext", "python3.12")
    main = next(f for f in result.files if f.path == "src/main.py")
    assert "def activate" in main.content
    assert "def deactivate" in main.content


def test_list_templates():
    svc = CLIGeneratorService()
    templates = svc.list_templates()
    runtimes = {t["runtime"] for t in templates}
    assert "node20" in runtimes
    assert "python3.12" in runtimes
    assert "deno" in runtimes
