"""App Version Migrator — manage version upgrades and rollbacks for installed apps.

Handles the lifecycle of app version transitions:
- Pre-upgrade compatibility checks
- Migration plan generation (config diff, permission diff, breaking changes)
- Rollback support with state snapshot
- Version pinning
- Upgrade history tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class MigrationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class CompatLevel(str, Enum):
    COMPATIBLE = "compatible"
    MINOR_CHANGES = "minor_changes"
    BREAKING = "breaking"


@dataclass
class VersionInfo:
    """Metadata for a specific app version."""

    version: str
    permissions: list[str]
    config_schema: dict[str, str]   # field_name → type
    min_platform_version: str | None = None
    changelog: str | None = None


@dataclass
class MigrationPlan:
    """Plan for upgrading between two versions."""

    from_version: str
    to_version: str
    compat_level: CompatLevel
    added_permissions: list[str]
    removed_permissions: list[str]
    added_config: list[str]
    removed_config: list[str]
    breaking_reasons: list[str]
    requires_reauth: bool      # new permissions need consent
    auto_migratable: bool      # can proceed without manual intervention


@dataclass
class MigrationRecord:
    """Record of a version migration."""

    migration_id: str
    installation_id: str
    from_version: str
    to_version: str
    status: MigrationStatus
    plan: MigrationPlan
    config_snapshot: dict       # config before migration (for rollback)
    permissions_snapshot: list[str]  # permissions before migration (for rollback)
    approved_permissions: set[str] = field(default_factory=set)  # admin-consented new permissions
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    error: str | None = None


@dataclass
class InstallationState:
    """Current state of an installed app."""

    installation_id: str
    app_id: str
    current_version: str
    pinned: bool = False
    config: dict = field(default_factory=dict)
    granted_permissions: list[str] = field(default_factory=list)


class AppVersionMigrator:
    """Plan, execute, and rollback app version upgrades."""

    def __init__(self):
        # (app_id, version) → VersionInfo
        self._versions: dict[tuple[str, str], VersionInfo] = {}
        # installation_id → InstallationState
        self._installations: dict[str, InstallationState] = {}
        # migration_id → MigrationRecord
        self._migrations: dict[str, MigrationRecord] = {}
        self._next_id = 0

    # ── Setup ────────────────────────────────────────────

    def register_version(self, app_id: str, info: VersionInfo) -> None:
        self._versions[(app_id, info.version)] = info

    def register_installation(self, state: InstallationState) -> None:
        self._installations[state.installation_id] = state

    # ── Planning ─────────────────────────────────────────

    def plan_upgrade(self, installation_id: str, target_version: str) -> MigrationPlan:
        """Generate a migration plan from current version to target."""
        state = self._installations.get(installation_id)
        if state is None:
            raise ValueError(f"Installation {installation_id} not found")

        old_info = self._versions.get((state.app_id, state.current_version))
        new_info = self._versions.get((state.app_id, target_version))
        if new_info is None:
            raise ValueError(f"Version {target_version} not found for app {state.app_id}")

        old_perms = set(old_info.permissions if old_info else [])
        new_perms = set(new_info.permissions)
        old_config = set(old_info.config_schema.keys() if old_info else [])
        new_config = set(new_info.config_schema.keys())

        added_perms = sorted(new_perms - old_perms)
        removed_perms = sorted(old_perms - new_perms)
        added_cfg = sorted(new_config - old_config)
        removed_cfg = sorted(old_config - new_config)

        breaking_reasons = []
        if removed_perms:
            breaking_reasons.append(f"Removed permissions: {', '.join(removed_perms)}")
        if removed_cfg:
            breaking_reasons.append(f"Removed config fields: {', '.join(removed_cfg)}")

        compat = CompatLevel.COMPATIBLE
        if breaking_reasons:
            compat = CompatLevel.BREAKING
        elif added_perms or added_cfg:
            compat = CompatLevel.MINOR_CHANGES

        return MigrationPlan(
            from_version=state.current_version,
            to_version=target_version,
            compat_level=compat,
            added_permissions=added_perms,
            removed_permissions=removed_perms,
            added_config=added_cfg,
            removed_config=removed_cfg,
            breaking_reasons=breaking_reasons,
            requires_reauth=len(added_perms) > 0,
            auto_migratable=compat != CompatLevel.BREAKING,
        )

    # ── Execution ────────────────────────────────────────

    def start_migration(self, installation_id: str, target_version: str,
                        consent_granted: bool = False,
                        approved_permissions: set[str] | None = None,
                        force: bool = False) -> MigrationRecord:
        """Start a version migration with consent and permission gates.

        consent_granted: admin has consented to new permissions (required when
            plan.requires_reauth is True).
        approved_permissions: the set of new permissions the admin approved —
            must come from an authenticated admin consent flow, not from the
            app manifest. Only these will be added on completion.
        force: allow breaking upgrades without auto_migratable (requires
            explicit admin approval).
        """
        state = self._installations.get(installation_id)
        if state is None:
            raise ValueError(f"Installation {installation_id} not found")

        if state.pinned:
            raise ValueError(f"Installation {installation_id} is version-pinned")

        plan = self.plan_upgrade(installation_id, target_version)

        # Gate: new permissions require explicit admin consent
        if plan.requires_reauth and not consent_granted:
            raise PermissionError(
                "New permissions require admin consent: "
                + ", ".join(plan.added_permissions)
            )

        # Gate: breaking changes require explicit force
        if not plan.auto_migratable and not force:
            raise ValueError(
                "Breaking upgrade requires manual approval (force=True): "
                + "; ".join(plan.breaking_reasons)
            )

        self._next_id += 1
        mid = f"mig-{self._next_id}"
        record = MigrationRecord(
            migration_id=mid,
            installation_id=installation_id,
            from_version=state.current_version,
            to_version=target_version,
            status=MigrationStatus.IN_PROGRESS,
            plan=plan,
            approved_permissions=approved_permissions or set(),
            config_snapshot=dict(state.config),
            permissions_snapshot=list(state.granted_permissions),
        )
        self._migrations[mid] = record
        log.info("migration.started", migration_id=mid, installation_id=installation_id,
                 from_version=state.current_version, to_version=target_version)
        return record

    def complete_migration(self, migration_id: str) -> MigrationRecord:
        """Mark a migration as completed and update the installation.

        Only permissions present in approved_permissions (from the admin
        consent flow) are actually added — the plan's added_permissions
        list is treated as the REQUEST, not the grant.
        """
        record = self._migrations.get(migration_id)
        if record is None:
            raise ValueError(f"Migration {migration_id} not found")

        if record.status != MigrationStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete migration in status {record.status.value}")

        record.status = MigrationStatus.COMPLETED
        record.completed_at = datetime.now(UTC)

        state = self._installations.get(record.installation_id)
        if state:
            state.current_version = record.to_version
            current = set(state.granted_permissions)
            # Only add permissions that were explicitly approved by admin
            approved_adds = set(record.plan.added_permissions) & record.approved_permissions
            current.update(approved_adds)
            # Remove old permissions
            current -= set(record.plan.removed_permissions)
            state.granted_permissions = sorted(current)

        log.info("migration.completed", migration_id=migration_id)
        return record

    def fail_migration(self, migration_id: str, error: str) -> MigrationRecord:
        """Mark a migration as failed."""
        record = self._migrations.get(migration_id)
        if record is None:
            raise ValueError(f"Migration {migration_id} not found")
        record.status = MigrationStatus.FAILED
        record.error = error
        record.completed_at = datetime.now(UTC)
        log.warning("migration.failed", migration_id=migration_id, error=error)
        return record

    def rollback(self, migration_id: str) -> MigrationRecord:
        """Rollback a completed or failed migration.

        Restores version, config, AND permissions from the pre-migration snapshot.
        """
        record = self._migrations.get(migration_id)
        if record is None:
            raise ValueError(f"Migration {migration_id} not found")

        if record.status not in (MigrationStatus.COMPLETED, MigrationStatus.FAILED):
            raise ValueError(f"Cannot rollback migration in status {record.status.value}")

        state = self._installations.get(record.installation_id)
        if state:
            state.current_version = record.from_version
            state.config = dict(record.config_snapshot)
            state.granted_permissions = list(record.permissions_snapshot)

        record.status = MigrationStatus.ROLLED_BACK
        record.completed_at = datetime.now(UTC)
        log.info("migration.rolled_back", migration_id=migration_id)
        return record

    # ── Pinning ──────────────────────────────────────────

    def pin_version(self, installation_id: str) -> None:
        state = self._installations.get(installation_id)
        if state:
            state.pinned = True

    def unpin_version(self, installation_id: str) -> None:
        state = self._installations.get(installation_id)
        if state:
            state.pinned = False

    # ── Querying ─────────────────────────────────────────

    def get_migration(self, migration_id: str) -> MigrationRecord | None:
        return self._migrations.get(migration_id)

    def get_history(self, installation_id: str) -> list[MigrationRecord]:
        return sorted(
            [m for m in self._migrations.values() if m.installation_id == installation_id],
            key=lambda m: m.started_at, reverse=True,
        )

    def get_installation(self, installation_id: str) -> InstallationState | None:
        return self._installations.get(installation_id)
