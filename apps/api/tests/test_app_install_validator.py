"""Tests for App Install Validator — pre-install checks, permissions, limits, dependencies."""

import pytest

from app.services.app_install_validator import (
    AppInstallValidator,
    AppManifest,
    CheckStatus,
    OrgContext,
)


def _manifest(**overrides) -> AppManifest:
    defaults = dict(app_id="app-1", app_name="Test App", version="1.0.0")
    defaults.update(overrides)
    return AppManifest(**defaults)


def _org(**overrides) -> OrgContext:
    defaults = dict(
        org_id="org-1",
        plan_max_apps=50,
        installed_app_ids=[],
        available_permissions={"read:skills", "write:projects", "read:email"},
        platform_version="2.0.0",
    )
    defaults.update(overrides)
    return OrgContext(**defaults)


class TestPassingValidation:
    def test_simple_app_passes(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(), _org())
        assert result.can_install is True
        assert result.error_count == 0

    def test_all_checks_pass(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(required_permissions=["read:skills"],
                      config_fields=["api_url"],
                      min_platform_version="1.0.0"),
            _org(),
            provided_config={"api_url": "https://example.com"},
        )
        assert result.can_install is True
        assert all(c.status in (CheckStatus.PASS, CheckStatus.WARN) for c in result.checks)


class TestReviewGate:
    def test_unpublished_app_fails(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(app_status="draft"), _org())
        assert result.can_install is False
        assert any("not published" in e for e in result.errors)

    def test_unapproved_version_fails(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(version_review_status="pending"), _org())
        assert result.can_install is False
        assert any("not approved" in e for e in result.errors)

    def test_revoked_app_fails(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(app_status="revoked"), _org())
        assert result.can_install is False

    def test_published_and_approved_passes(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(app_status="published", version_review_status="approved"), _org())
        check = [c for c in result.checks if c.name == "review"][0]
        assert check.status == CheckStatus.PASS


class TestBlocklist:
    def test_blocked_app_fails(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(), _org(blocklist={"app-1"}))
        assert result.can_install is False
        assert any("blocked" in e for e in result.errors)

    def test_unblocked_app_passes(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(), _org(blocklist={"app-99"}))
        assert result.can_install is True


class TestAllowlist:
    def test_not_in_allowlist_fails(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(), _org(allowlist={"app-99"}))
        assert result.can_install is False
        assert any("allowlist" in e for e in result.errors)

    def test_in_allowlist_passes(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(), _org(allowlist={"app-1"}))
        assert result.can_install is True

    def test_no_allowlist_passes(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(), _org(allowlist=None))
        assert result.can_install is True


class TestDuplicate:
    def test_already_installed_fails(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(), _org(installed_app_ids=["app-1"]))
        assert result.can_install is False
        assert any("already installed" in e for e in result.errors)


class TestPlanLimit:
    def test_at_limit_fails(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(), _org(plan_max_apps=3, installed_app_ids=["a", "b", "c"]))
        assert result.can_install is False
        assert any("limit" in e for e in result.errors)

    def test_near_limit_warns(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(),
            _org(plan_max_apps=10, installed_app_ids=[f"a{i}" for i in range(9)]),
        )
        assert result.can_install is True
        assert result.warning_count >= 1
        assert any("near" in w for w in result.warnings)

    def test_under_limit_passes(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(), _org(plan_max_apps=50))
        check = [c for c in result.checks if c.name == "plan_limit"][0]
        assert check.status == CheckStatus.PASS


class TestPlatformVersion:
    def test_incompatible_version_fails(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(min_platform_version="3.0.0"),
            _org(platform_version="2.0.0"),
        )
        assert result.can_install is False
        assert any("platform" in e.lower() for e in result.errors)

    def test_compatible_version_passes(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(min_platform_version="1.0.0"),
            _org(platform_version="2.0.0"),
        )
        check = [c for c in result.checks if c.name == "platform_version"][0]
        assert check.status == CheckStatus.PASS

    def test_no_version_requirement_passes(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(min_platform_version=None), _org())
        check = [c for c in result.checks if c.name == "platform_version"][0]
        assert check.status == CheckStatus.PASS


class TestPermissions:
    def test_missing_permissions_fails(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(required_permissions=["admin:org"]),
            _org(available_permissions={"read:skills"}),
        )
        assert result.can_install is False
        assert any("admin:org" in e for e in result.errors)

    def test_all_permissions_available(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(required_permissions=["read:skills"]),
            _org(),
        )
        check = [c for c in result.checks if c.name == "permissions"][0]
        assert check.status == CheckStatus.PASS


class TestConfig:
    def test_missing_config_fails(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(config_fields=["api_url", "secret"]),
            _org(),
            provided_config={"api_url": "https://x.com"},
        )
        assert result.can_install is False
        assert any("secret" in e for e in result.errors)

    def test_no_config_provided_warns(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(config_fields=["api_url"]),
            _org(),
            provided_config=None,
        )
        assert result.can_install is True
        assert result.warning_count >= 1

    def test_all_config_provided(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(config_fields=["api_url"]),
            _org(),
            provided_config={"api_url": "https://x.com"},
        )
        check = [c for c in result.checks if c.name == "config"][0]
        assert check.status == CheckStatus.PASS


class TestDependencies:
    def test_missing_dependency_fails(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(dependencies=["app-base"]),
            _org(installed_app_ids=[]),
        )
        assert result.can_install is False
        assert any("app-base" in e for e in result.errors)

    def test_dependency_installed(self):
        v = AppInstallValidator()
        result = v.validate(
            _manifest(dependencies=["app-base"]),
            _org(installed_app_ids=["app-base"]),
        )
        check = [c for c in result.checks if c.name == "dependencies"][0]
        assert check.status == CheckStatus.PASS

    def test_no_dependencies(self):
        v = AppInstallValidator()
        result = v.validate(_manifest(dependencies=[]), _org())
        check = [c for c in result.checks if c.name == "dependencies"][0]
        assert check.status == CheckStatus.PASS
