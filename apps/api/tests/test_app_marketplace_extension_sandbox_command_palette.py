from app.services.app_marketplace_extension_sandbox_command_palette import (
    SandboxCommandPaletteService,
)
import pytest


def test_register_and_search():
    svc = SandboxCommandPaletteService()
    svc.register("sb-1", "format", "Format Document", "editor",
                 shortcut="Ctrl+Shift+F")
    results = svc.search("sb-1", "format")
    assert len(results) == 1
    assert results[0].title == "Format Document"


def test_fuzzy_search():
    svc = SandboxCommandPaletteService()
    svc.register("sb-1", "open_file", "Open File", "file")
    svc.register("sb-1", "open_term", "Open Terminal", "terminal")
    svc.register("sb-1", "save_file", "Save File", "file")
    results = svc.search("sb-1", "open")
    assert len(results) == 2


def test_execute():
    svc = SandboxCommandPaletteService()
    svc.register("sb-1", "build", "Build Project", "project", handler="run_build")
    result = svc.execute("sb-1", "build")
    assert result["ok"] is True
    assert result["handler"] == "run_build"


def test_shortcut_lookup():
    svc = SandboxCommandPaletteService()
    svc.register("sb-1", "save", "Save", "file", shortcut="Ctrl+S")
    cmd = svc.get_by_shortcut("sb-1", "Ctrl+S")
    assert cmd is not None
    assert cmd.command_id == "save"


def test_categories():
    svc = SandboxCommandPaletteService()
    svc.register("sb-1", "a", "A", "editor")
    svc.register("sb-1", "b", "B", "file")
    svc.register("sb-1", "c", "C", "editor")
    cats = svc.get_categories("sb-1")
    assert cats == ["editor", "file"]
    assert len(svc.get_by_category("sb-1", "editor")) == 2


def test_recent_history():
    svc = SandboxCommandPaletteService()
    svc.register("sb-1", "a", "A", "cat")
    svc.register("sb-1", "b", "B", "cat")
    svc.execute("sb-1", "a")
    svc.execute("sb-1", "b")
    svc.execute("sb-1", "a")
    recent = svc.get_recent("sb-1", 2)
    assert recent[0].command_id == "a"  # most recent first


def test_disable():
    svc = SandboxCommandPaletteService()
    svc.register("sb-1", "cmd", "Cmd", "cat")
    svc.disable("sb-1", "cmd")
    result = svc.execute("sb-1", "cmd")
    assert result["ok"] is False


def test_duplicate_rejected():
    svc = SandboxCommandPaletteService()
    svc.register("sb-1", "cmd", "Cmd", "cat")
    with pytest.raises(ValueError, match="already registered"):
        svc.register("sb-1", "cmd", "Dup", "cat")
