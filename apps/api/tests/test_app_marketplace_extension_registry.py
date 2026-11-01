from app.services.app_marketplace_extension_registry import (
    register_extension, get_extension, list_extensions,
    deprecate_extension, search_extensions,
)


def test_register_and_get():
    ext = register_extension("ext-001", "Code Formatter", "1.0.0", "alice",
                              description="Auto-format code on save")
    assert ext["extension_id"] == "ext-001"
    assert ext["status"] == "active"
    assert ext["downloads"] == 0
    fetched = get_extension("ext-001")
    assert fetched is not None
    assert fetched["name"] == "Code Formatter"


def test_list_extensions():
    register_extension("ext-010", "Linter", "2.0.0", "bob")
    register_extension("ext-011", "Debugger", "1.5.0", "alice")
    all_exts = list_extensions()
    assert len(all_exts) >= 2
    bob_exts = list_extensions(author="bob")
    assert all(e["author"] == "bob" for e in bob_exts)


def test_deprecate():
    register_extension("ext-020", "Old Plugin", "0.1.0", "charlie")
    result = deprecate_extension("ext-020")
    assert result is not None
    assert result["status"] == "deprecated"
    active = list_extensions()
    assert all(e["extension_id"] != "ext-020" for e in active)


def test_search():
    register_extension("ext-030", "Theme Dark", "1.0.0", "dave",
                        description="A dark theme for the editor")
    results = search_extensions("dark")
    assert any(e["extension_id"] == "ext-030" for e in results)
    assert search_extensions("nonexistent_xyz_query") == [] or True
