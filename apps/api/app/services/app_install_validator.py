"""App Install Validator — pre-installation checks for developer apps.

Validates that an app can be safely installed into an org:
- Platform version compatibility
- Required permission availability
- Config schema completeness
- Dependency satisfaction
- Existing installation conflict detection
- Org plan limits (max installed apps)
- Blocklist/allowlist enforcement
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


@dataclass
class ValidationCheck:
    """A single validation check result."""

    name: str
    status: CheckStatus
    message: str


@dataclass
class InstallValidationResult:
    """Complete pre-install validation result."""

    can_install: bool
    checks: list[ValidationCheck]
    errors: list[str]
    warnings: list[str]

    @property
    def error_count(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.FAIL)

    @property
    def warning_count(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.WARN)


@dataclass
class AppManifest:
    """Simplified manifest for validation.

    app_status and version_review_status MUST be populated server-side
    from the DB, never from the developer-supplied manifest.
    """

    app_id: str
    app_name: str
    version: str
    app_status: str | None = None               # server-side: draft/published/suspended/revoked — None = fail-closed
    version_review_status: str | None = None    # server-side: pending/approved/rejected/revoked — None = fail-closed
    min_platform_version: str | None = None
    required_permissions: list[str] = field(default_factory=list)
    config_fields: list[str] = field(default_factory=list)     # required config field names
    dependencies: list[str] = field(default_factory=list)       # app_ids this app depends on


@dataclass
class OrgContext:
    """Organization context for install validation."""

    org_id: str
    plan_max_apps: int = 50
    installed_app_ids: list[str] = field(default_factory=list)
    available_permissions: set[str] = field(default_factory=set)
    platform_version: str = "1.0.0"
    blocklist: set[str] = field(default_factory=set)   # blocked app_ids
    allowlist: set[str] | None = None                    # if set, only these allowed


class AppInstallValidator:
    """Run pre-installation validation checks."""

    def validate(self, manifest: AppManifest, org: OrgContext,
                 provided_config: dict | None = None) -> InstallValidationResult:
        """Run all validation checks and return the result."""
        checks: list[ValidationCheck] = []

        checks.append(self._check_review(manifest))
        checks.append(self._check_blocklist(manifest, org))
        checks.append(self._check_allowlist(manifest, org))
        checks.append(self._check_duplicate(manifest, org))
        checks.append(self._check_plan_limit(org))
        checks.append(self._check_platform_version(manifest, org))
        checks.append(self._check_permissions(manifest, org))
        checks.append(self._check_config(manifest, provided_config))
        checks.append(self._check_dependencies(manifest, org))

        errors = [c.message for c in checks if c.status == CheckStatus.FAIL]
        warnings = [c.message for c in checks if c.status == CheckStatus.WARN]
        can_install = len(errors) == 0

        return InstallValidationResult(
            can_install=can_install,
            checks=checks,
            errors=errors,
            warnings=warnings,
        )

    # ── Individual checks ────────────────────────────────

    @staticmethod
    def _check_review(manifest: AppManifest) -> ValidationCheck:
        """Gate: only published+approved apps can be installed.

        app_status and version_review_status are populated server-side
        from the DB, not from the developer-supplied manifest.
        Fail-closed: None or unexpected values always reject.
        """
        if manifest.app_status is None or manifest.app_status != "published":
            return ValidationCheck("review", CheckStatus.FAIL,
                                   f"App is not published (status: {manifest.app_status})")
        if manifest.version_review_status is None or manifest.version_review_status != "approved":
            return ValidationCheck("review", CheckStatus.FAIL,
                                   f"App version not approved (review: {manifest.version_review_status})")
        return ValidationCheck("review", CheckStatus.PASS, "App is published and version approved")

    @staticmethod
    def _check_blocklist(manifest: AppManifest, org: OrgContext) -> ValidationCheck:
        if manifest.app_id in org.blocklist:
            return ValidationCheck("blocklist", CheckStatus.FAIL,
                                   f"App {manifest.app_id} is blocked for this organization")
        return ValidationCheck("blocklist", CheckStatus.PASS, "App is not blocked")

    @staticmethod
    def _check_allowlist(manifest: AppManifest, org: OrgContext) -> ValidationCheck:
        if org.allowlist is not None and manifest.app_id not in org.allowlist:
            return ValidationCheck("allowlist", CheckStatus.FAIL,
                                   f"App {manifest.app_id} is not in the org allowlist")
        return ValidationCheck("allowlist", CheckStatus.PASS, "Allowlist check passed")

    @staticmethod
    def _check_duplicate(manifest: AppManifest, org: OrgContext) -> ValidationCheck:
        if manifest.app_id in org.installed_app_ids:
            return ValidationCheck("duplicate", CheckStatus.FAIL,
                                   f"App {manifest.app_id} is already installed")
        return ValidationCheck("duplicate", CheckStatus.PASS, "No duplicate installation")

    @staticmethod
    def _check_plan_limit(org: OrgContext) -> ValidationCheck:
        current = len(org.installed_app_ids)
        if current >= org.plan_max_apps:
            return ValidationCheck("plan_limit", CheckStatus.FAIL,
                                   f"Org has reached the app limit ({current}/{org.plan_max_apps})")
        if current >= org.plan_max_apps * 0.9:
            return ValidationCheck("plan_limit", CheckStatus.WARN,
                                   f"Org is near the app limit ({current}/{org.plan_max_apps})")
        return ValidationCheck("plan_limit", CheckStatus.PASS,
                               f"Within app limit ({current}/{org.plan_max_apps})")

    @staticmethod
    def _check_platform_version(manifest: AppManifest, org: OrgContext) -> ValidationCheck:
        if not manifest.min_platform_version:
            return ValidationCheck("platform_version", CheckStatus.PASS,
                                   "No minimum platform version required")
        if manifest.min_platform_version > org.platform_version:
            return ValidationCheck("platform_version", CheckStatus.FAIL,
                                   f"Requires platform >= {manifest.min_platform_version}, "
                                   f"current is {org.platform_version}")
        return ValidationCheck("platform_version", CheckStatus.PASS,
                               f"Platform {org.platform_version} meets requirement "
                               f"{manifest.min_platform_version}")

    @staticmethod
    def _check_permissions(manifest: AppManifest, org: OrgContext) -> ValidationCheck:
        if not manifest.required_permissions:
            return ValidationCheck("permissions", CheckStatus.PASS, "No permissions required")
        missing = set(manifest.required_permissions) - org.available_permissions
        if missing:
            return ValidationCheck("permissions", CheckStatus.FAIL,
                                   f"Missing permissions: {', '.join(sorted(missing))}")
        return ValidationCheck("permissions", CheckStatus.PASS,
                               f"All {len(manifest.required_permissions)} permissions available")

    @staticmethod
    def _check_config(manifest: AppManifest, provided_config: dict | None) -> ValidationCheck:
        if not manifest.config_fields:
            return ValidationCheck("config", CheckStatus.PASS, "No config required")
        if provided_config is None:
            return ValidationCheck("config", CheckStatus.WARN,
                                   "Config not provided — will use defaults if available")
        missing = [f for f in manifest.config_fields if f not in provided_config]
        if missing:
            return ValidationCheck("config", CheckStatus.FAIL,
                                   f"Missing config fields: {', '.join(missing)}")
        return ValidationCheck("config", CheckStatus.PASS,
                               f"All {len(manifest.config_fields)} config fields provided")

    @staticmethod
    def _check_dependencies(manifest: AppManifest, org: OrgContext) -> ValidationCheck:
        if not manifest.dependencies:
            return ValidationCheck("dependencies", CheckStatus.PASS, "No dependencies")
        missing = [d for d in manifest.dependencies if d not in org.installed_app_ids]
        if missing:
            return ValidationCheck("dependencies", CheckStatus.FAIL,
                                   f"Missing dependencies: {', '.join(missing)}")
        return ValidationCheck("dependencies", CheckStatus.PASS,
                               f"All {len(manifest.dependencies)} dependencies installed")
