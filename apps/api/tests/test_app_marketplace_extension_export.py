from app.services.app_marketplace_extension_export import ExtensionExporter


SAMPLE_FILES = {
    "manifest.json": '{"name": "test-ext", "version": "1.0.0"}',
    "src/main.py": "def run(): pass",
    "README.md": "# Test Extension",
}


def test_build_package():
    exp = ExtensionExporter()
    manifest, msg = exp.build_package("ext-1", "1.0.0", SAMPLE_FILES)
    assert manifest is not None
    assert len(manifest.files) == 3
    assert manifest.total_size_bytes > 0
    assert len(manifest.checksum) == 64  # SHA-256


def test_missing_manifest():
    exp = ExtensionExporter()
    files = {"src/main.py": "code"}
    manifest, msg = exp.build_package("ext-2", "1.0.0", files)
    assert manifest is None
    assert "Missing manifest" in msg


def test_empty_files():
    exp = ExtensionExporter()
    manifest, msg = exp.build_package("ext-3", "1.0.0", {})
    assert manifest is None


def test_verify_checksum():
    exp = ExtensionExporter()
    exp.build_package("ext-4", "1.0.0", SAMPLE_FILES)
    assert exp.verify_checksum("ext-4", "1.0.0", SAMPLE_FILES) is True
    # Tampered content
    tampered = {**SAMPLE_FILES, "src/main.py": "TAMPERED"}
    assert exp.verify_checksum("ext-4", "1.0.0", tampered) is False


def test_list_exports():
    exp = ExtensionExporter()
    exp.build_package("ext-5", "1.0.0", SAMPLE_FILES)
    exp.build_package("ext-5", "1.1.0", SAMPLE_FILES)
    exports = exp.list_exports("ext-5")
    assert len(exports) == 2


def test_get_manifest():
    exp = ExtensionExporter()
    exp.build_package("ext-6", "2.0.0", SAMPLE_FILES)
    m = exp.get_manifest("ext-6", "2.0.0")
    assert m is not None
    assert m.version == "2.0.0"
    assert m.format == "tar.gz"
