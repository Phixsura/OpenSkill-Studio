"""Extension Point Registry — manage UI and API extension points for the developer platform.

Catalogs all extension surfaces that third-party apps can plug into:
- UI surfaces: sidebar, settings panel, dashboard widget, etc.
- API hooks: pre/post request, event handler, data transformer
- Slot-based registration: each surface has typed slots
- Priority ordering for multiple extensions on the same slot
- Conflict detection (two apps claiming the same exclusive slot)
- Extension manifest validation against registered surfaces
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class SurfaceType(str, Enum):
    UI_SIDEBAR = "ui_sidebar"
    UI_SETTINGS = "ui_settings"
    UI_DASHBOARD_WIDGET = "ui_dashboard_widget"
    UI_PROJECT_TAB = "ui_project_tab"
    UI_SUBMISSION_PANEL = "ui_submission_panel"
    UI_TOOLBAR_ACTION = "ui_toolbar_action"
    API_PRE_HOOK = "api_pre_hook"
    API_POST_HOOK = "api_post_hook"
    API_EVENT_HANDLER = "api_event_handler"
    API_DATA_TRANSFORMER = "api_data_transformer"
    EVAL_RUBRIC = "eval_rubric"
    PROVIDER_ADAPTER = "provider_adapter"


class SlotMode(str, Enum):
    MULTIPLE = "multiple"    # many extensions can register
    EXCLUSIVE = "exclusive"  # only one extension can claim


@dataclass
class ExtensionSlot:
    """A slot within a surface that extensions can fill."""

    slot_id: str
    surface: SurfaceType
    label: str
    description: str
    mode: SlotMode = SlotMode.MULTIPLE
    max_extensions: int = 10      # for MULTIPLE mode
    required_permissions: list[str] = field(default_factory=list)
    schema: dict | None = None    # JSON schema the extension must conform to


@dataclass
class RegisteredExtension:
    """An extension registered to a slot by an app."""

    app_id: str
    app_name: str
    slot_id: str
    surface: SurfaceType
    priority: int = 0        # lower = higher priority
    config: dict = field(default_factory=dict)
    enabled: bool = True


@dataclass
class ConflictInfo:
    """Info about a slot conflict."""

    slot_id: str
    existing_app_id: str
    existing_app_name: str
    reason: str


@dataclass
class RegistrationResult:
    """Result of attempting to register an extension."""

    success: bool
    extension: RegisteredExtension | None = None
    conflict: ConflictInfo | None = None
    error: str | None = None


@dataclass
class SlotStatus:
    """Current status of a slot."""

    slot: ExtensionSlot
    extensions: list[RegisteredExtension]
    available_capacity: int
    is_full: bool


class ExtensionPointRegistry:
    """Manage extension surfaces and slot registrations."""

    def __init__(self):
        # slot_id → ExtensionSlot
        self._slots: dict[str, ExtensionSlot] = {}
        # slot_id → list of registered extensions (ordered by priority)
        self._registrations: dict[str, list[RegisteredExtension]] = {}

    # ── Slot management ──────────────────────────────────

    def define_slot(self, slot: ExtensionSlot) -> None:
        """Register a new extension slot."""
        self._slots[slot.slot_id] = slot
        if slot.slot_id not in self._registrations:
            self._registrations[slot.slot_id] = []

    def get_slot(self, slot_id: str) -> ExtensionSlot | None:
        return self._slots.get(slot_id)

    def list_slots(self, surface: SurfaceType | None = None) -> list[ExtensionSlot]:
        slots = list(self._slots.values())
        if surface:
            slots = [s for s in slots if s.surface == surface]
        return sorted(slots, key=lambda s: s.slot_id)

    def list_surfaces(self) -> list[SurfaceType]:
        """List all surfaces that have at least one slot defined."""
        surfaces = {s.surface for s in self._slots.values()}
        return sorted(surfaces, key=lambda s: s.value)

    # ── Extension registration ───────────────────────────

    def register(self, app_id: str, app_name: str, slot_id: str,
                 priority: int = 0, config: dict | None = None,
                 granted_permissions: set[str] | None = None) -> RegistrationResult:
        """Register an extension to a slot.

        granted_permissions should come from the server-side app installation
        record, NOT from the app-supplied manifest. Slots with
        required_permissions will deny registration if any are missing.
        """
        slot = self._slots.get(slot_id)
        if slot is None:
            return RegistrationResult(
                success=False, error=f"Unknown slot: {slot_id}"
            )

        # Permission check: deny if the slot requires permissions the app doesn't have
        if slot.required_permissions:
            actual = granted_permissions or set()
            missing = set(slot.required_permissions) - actual
            if missing:
                return RegistrationResult(
                    success=False,
                    error=f"Missing permissions: {', '.join(sorted(missing))}",
                )

        existing = self._registrations.get(slot_id, [])

        # Check exclusive slot conflict
        if slot.mode == SlotMode.EXCLUSIVE and existing:
            current = existing[0]
            if current.app_id != app_id:
                return RegistrationResult(
                    success=False,
                    conflict=ConflictInfo(
                        slot_id=slot_id,
                        existing_app_id=current.app_id,
                        existing_app_name=current.app_name,
                        reason=f"Exclusive slot already claimed by {current.app_name}",
                    ),
                )

        # Check capacity for multiple slots
        if slot.mode == SlotMode.MULTIPLE:
            active = [e for e in existing if e.enabled]
            if len(active) >= slot.max_extensions:
                return RegistrationResult(
                    success=False,
                    error=f"Slot {slot_id} is full ({slot.max_extensions} max)",
                )

        # Check duplicate
        if any(e.app_id == app_id for e in existing):
            return RegistrationResult(
                success=False,
                error=f"App {app_id} already registered on slot {slot_id}",
            )

        ext = RegisteredExtension(
            app_id=app_id,
            app_name=app_name,
            slot_id=slot_id,
            surface=slot.surface,
            priority=priority,
            config=config or {},
        )
        existing.append(ext)
        existing.sort(key=lambda e: e.priority)
        self._registrations[slot_id] = existing

        log.info("extension.registered", app_id=app_id, slot_id=slot_id)
        return RegistrationResult(success=True, extension=ext)

    def unregister(self, app_id: str, slot_id: str) -> bool:
        """Remove an app's extension from a slot."""
        existing = self._registrations.get(slot_id, [])
        before = len(existing)
        self._registrations[slot_id] = [e for e in existing if e.app_id != app_id]
        removed = len(self._registrations[slot_id]) < before
        if removed:
            log.info("extension.unregistered", app_id=app_id, slot_id=slot_id)
        return removed

    def unregister_app(self, app_id: str) -> int:
        """Remove all extensions for an app (e.g. on uninstall). Returns count removed."""
        total = 0
        for slot_id in list(self._registrations.keys()):
            existing = self._registrations[slot_id]
            before = len(existing)
            self._registrations[slot_id] = [e for e in existing if e.app_id != app_id]
            total += before - len(self._registrations[slot_id])
        return total

    # ── Querying ─────────────────────────────────────────

    def get_extensions(self, slot_id: str, enabled_only: bool = True) -> list[RegisteredExtension]:
        """Get all extensions for a slot, ordered by priority."""
        exts = self._registrations.get(slot_id, [])
        if enabled_only:
            exts = [e for e in exts if e.enabled]
        return exts

    def get_app_extensions(self, app_id: str) -> list[RegisteredExtension]:
        """Get all extensions registered by an app across all slots."""
        result = []
        for exts in self._registrations.values():
            for e in exts:
                if e.app_id == app_id:
                    result.append(e)
        return sorted(result, key=lambda e: e.slot_id)

    def get_slot_status(self, slot_id: str) -> SlotStatus | None:
        """Get current status of a slot including capacity."""
        slot = self._slots.get(slot_id)
        if slot is None:
            return None
        exts = self._registrations.get(slot_id, [])
        active = [e for e in exts if e.enabled]
        cap = slot.max_extensions - len(active) if slot.mode == SlotMode.MULTIPLE else (0 if active else 1)
        return SlotStatus(
            slot=slot, extensions=active,
            available_capacity=max(0, cap),
            is_full=cap <= 0,
        )

    def validate_manifest_surfaces(self, surfaces: list[str]) -> tuple[list[str], list[str]]:
        """Validate that all requested surfaces exist.

        Returns (valid, invalid) slot ID lists.
        """
        valid = [s for s in surfaces if s in self._slots]
        invalid = [s for s in surfaces if s not in self._slots]
        return valid, invalid
