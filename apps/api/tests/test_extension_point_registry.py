"""Tests for Extension Point Registry — slot management, registration, conflicts."""

import pytest

from app.services.extension_point_registry import (
    ExtensionPointRegistry,
    ExtensionSlot,
    SlotMode,
    SurfaceType,
)


def _setup_registry() -> ExtensionPointRegistry:
    reg = ExtensionPointRegistry()
    reg.define_slot(ExtensionSlot(
        slot_id="sidebar_nav", surface=SurfaceType.UI_SIDEBAR,
        label="Sidebar Navigation", description="Add items to the sidebar",
        mode=SlotMode.MULTIPLE, max_extensions=5,
    ))
    reg.define_slot(ExtensionSlot(
        slot_id="settings_auth", surface=SurfaceType.UI_SETTINGS,
        label="Auth Settings", description="Custom auth settings panel",
        mode=SlotMode.EXCLUSIVE,
    ))
    reg.define_slot(ExtensionSlot(
        slot_id="dashboard_widget", surface=SurfaceType.UI_DASHBOARD_WIDGET,
        label="Dashboard Widget", description="Add a dashboard widget",
        mode=SlotMode.MULTIPLE, max_extensions=3,
    ))
    return reg


class TestSlotManagement:
    def test_define_and_get_slot(self):
        reg = _setup_registry()
        slot = reg.get_slot("sidebar_nav")
        assert slot is not None
        assert slot.label == "Sidebar Navigation"
        assert slot.mode == SlotMode.MULTIPLE

    def test_get_nonexistent_slot(self):
        reg = _setup_registry()
        assert reg.get_slot("nonexistent") is None

    def test_list_all_slots(self):
        reg = _setup_registry()
        slots = reg.list_slots()
        assert len(slots) == 3
        assert [s.slot_id for s in slots] == ["dashboard_widget", "settings_auth", "sidebar_nav"]

    def test_list_slots_by_surface(self):
        reg = _setup_registry()
        ui_sidebar = reg.list_slots(SurfaceType.UI_SIDEBAR)
        assert len(ui_sidebar) == 1
        assert ui_sidebar[0].slot_id == "sidebar_nav"

    def test_list_surfaces(self):
        reg = _setup_registry()
        surfaces = reg.list_surfaces()
        assert SurfaceType.UI_SIDEBAR in surfaces
        assert SurfaceType.UI_SETTINGS in surfaces


class TestRegistration:
    def test_register_success(self):
        reg = _setup_registry()
        result = reg.register("app-1", "My App", "sidebar_nav")
        assert result.success is True
        assert result.extension is not None
        assert result.extension.app_id == "app-1"

    def test_register_unknown_slot(self):
        reg = _setup_registry()
        result = reg.register("app-1", "My App", "nonexistent_slot")
        assert result.success is False
        assert "Unknown slot" in (result.error or "")

    def test_register_duplicate_blocked(self):
        reg = _setup_registry()
        reg.register("app-1", "My App", "sidebar_nav")
        result = reg.register("app-1", "My App", "sidebar_nav")
        assert result.success is False
        assert "already registered" in (result.error or "")

    def test_multiple_apps_on_same_slot(self):
        reg = _setup_registry()
        reg.register("app-1", "App 1", "sidebar_nav")
        result = reg.register("app-2", "App 2", "sidebar_nav")
        assert result.success is True

    def test_priority_ordering(self):
        reg = _setup_registry()
        reg.register("app-2", "Low Priority", "sidebar_nav", priority=10)
        reg.register("app-1", "High Priority", "sidebar_nav", priority=1)
        exts = reg.get_extensions("sidebar_nav")
        assert exts[0].app_id == "app-1"
        assert exts[1].app_id == "app-2"


class TestExclusiveSlot:
    def test_exclusive_first_succeeds(self):
        reg = _setup_registry()
        result = reg.register("app-1", "Auth App", "settings_auth")
        assert result.success is True

    def test_exclusive_second_conflicts(self):
        reg = _setup_registry()
        reg.register("app-1", "Auth App 1", "settings_auth")
        result = reg.register("app-2", "Auth App 2", "settings_auth")
        assert result.success is False
        assert result.conflict is not None
        assert result.conflict.existing_app_id == "app-1"
        assert "Exclusive" in result.conflict.reason

    def test_exclusive_same_app_conflicts(self):
        reg = _setup_registry()
        reg.register("app-1", "Auth App", "settings_auth")
        result = reg.register("app-1", "Auth App", "settings_auth")
        assert result.success is False  # duplicate, not conflict


class TestCapacity:
    def test_capacity_limit(self):
        reg = _setup_registry()
        for i in range(3):
            result = reg.register(f"app-{i}", f"App {i}", "dashboard_widget")
            assert result.success is True
        # 4th should fail (max 3)
        result = reg.register("app-3", "App 3", "dashboard_widget")
        assert result.success is False
        assert "full" in (result.error or "")

    def test_slot_status_capacity(self):
        reg = _setup_registry()
        reg.register("app-1", "App 1", "dashboard_widget")
        status = reg.get_slot_status("dashboard_widget")
        assert status is not None
        assert status.available_capacity == 2
        assert status.is_full is False

    def test_slot_status_full(self):
        reg = _setup_registry()
        for i in range(3):
            reg.register(f"app-{i}", f"App {i}", "dashboard_widget")
        status = reg.get_slot_status("dashboard_widget")
        assert status.is_full is True
        assert status.available_capacity == 0


class TestUnregister:
    def test_unregister(self):
        reg = _setup_registry()
        reg.register("app-1", "App 1", "sidebar_nav")
        removed = reg.unregister("app-1", "sidebar_nav")
        assert removed is True
        assert len(reg.get_extensions("sidebar_nav")) == 0

    def test_unregister_nonexistent(self):
        reg = _setup_registry()
        assert reg.unregister("app-99", "sidebar_nav") is False

    def test_unregister_app_all_slots(self):
        reg = _setup_registry()
        reg.register("app-1", "App 1", "sidebar_nav")
        reg.register("app-1", "App 1", "dashboard_widget")
        count = reg.unregister_app("app-1")
        assert count == 2
        assert len(reg.get_app_extensions("app-1")) == 0

    def test_unregister_frees_exclusive_slot(self):
        reg = _setup_registry()
        reg.register("app-1", "App 1", "settings_auth")
        reg.unregister("app-1", "settings_auth")
        result = reg.register("app-2", "App 2", "settings_auth")
        assert result.success is True


class TestQuerying:
    def test_get_app_extensions(self):
        reg = _setup_registry()
        reg.register("app-1", "App 1", "sidebar_nav")
        reg.register("app-1", "App 1", "dashboard_widget")
        exts = reg.get_app_extensions("app-1")
        assert len(exts) == 2
        slot_ids = [e.slot_id for e in exts]
        assert "sidebar_nav" in slot_ids
        assert "dashboard_widget" in slot_ids

    def test_get_extensions_empty(self):
        reg = _setup_registry()
        assert reg.get_extensions("sidebar_nav") == []

    def test_slot_status_nonexistent(self):
        reg = _setup_registry()
        assert reg.get_slot_status("nonexistent") is None


class TestManifestValidation:
    def test_validate_valid_surfaces(self):
        reg = _setup_registry()
        valid, invalid = reg.validate_manifest_surfaces(["sidebar_nav", "dashboard_widget"])
        assert valid == ["sidebar_nav", "dashboard_widget"]
        assert invalid == []

    def test_validate_mixed(self):
        reg = _setup_registry()
        valid, invalid = reg.validate_manifest_surfaces(["sidebar_nav", "nonexistent"])
        assert valid == ["sidebar_nav"]
        assert invalid == ["nonexistent"]

    def test_validate_all_invalid(self):
        reg = _setup_registry()
        valid, invalid = reg.validate_manifest_surfaces(["a", "b"])
        assert valid == []
        assert invalid == ["a", "b"]
