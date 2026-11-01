"""Tests for App Sandbox Policy Engine — network, filesystem, env, secret, composition."""

import pytest

from app.services.app_sandbox_policy_engine import (
    AppSandboxPolicyEngine,
    FilesystemRule,
    NetworkProtocol,
    NetworkRule,
    PolicyAction,
    SandboxPolicy,
)


def _app_policy() -> SandboxPolicy:
    return SandboxPolicy(
        app_id="app-1",
        network_rules=[
            NetworkRule("api.example.com", PolicyAction.ALLOW),
            NetworkRule("*.cdn.example.com", PolicyAction.ALLOW),
            NetworkRule("evil.com", PolicyAction.DENY),
        ],
        filesystem_rules=[
            FilesystemRule("/tmp/sandbox/", readable=True, writable=True),
            FilesystemRule("/data/readonly/", readable=True, writable=False),
        ],
        allowed_env_vars=["NODE_ENV", "TZ", "API_URL"],
        allowed_secret_keys=["API_KEY", "DB_PASSWORD"],
        max_execution_seconds=60,
        max_memory_mb=256,
        allow_subprocess=False,
    )


class TestNetworkPolicy:
    def test_allowed_domain(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_network("app-1", "api.example.com")
        assert r.allowed is True

    def test_denied_domain(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_network("app-1", "evil.com")
        assert r.allowed is False

    def test_wildcard_subdomain(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_network("app-1", "images.cdn.example.com")
        assert r.allowed is True

    def test_wildcard_exact_domain(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_network("app-1", "cdn.example.com")
        assert r.allowed is True

    def test_default_deny(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_network("app-1", "unknown.com")
        assert r.allowed is False
        assert "default_deny" in r.rule_matched

    def test_wrong_protocol_denied(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_network("app-1", "api.example.com", NetworkProtocol.HTTP)
        assert r.allowed is False
        assert "Protocol" in r.rule_matched

    def test_unregistered_app_default_deny(self):
        e = AppSandboxPolicyEngine()
        r = e.check_network("unknown-app", "anywhere.com")
        assert r.allowed is False


class TestFilesystemPolicy:
    def test_read_allowed(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_filesystem("app-1", "/tmp/sandbox/data.json")
        assert r.allowed is True

    def test_write_allowed_on_writable(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_filesystem("app-1", "/tmp/sandbox/output.json", write=True)
        assert r.allowed is True

    def test_write_denied_on_readonly(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_filesystem("app-1", "/data/readonly/file.txt", write=True)
        assert r.allowed is False

    def test_unmatched_path_denied(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_filesystem("app-1", "/etc/passwd")
        assert r.allowed is False

    def test_read_from_readonly(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        r = e.check_filesystem("app-1", "/data/readonly/config.yaml")
        assert r.allowed is True


class TestEnvVarPolicy:
    def test_allowed_env_var(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        assert e.check_env_var("app-1", "NODE_ENV").allowed is True

    def test_denied_env_var(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        assert e.check_env_var("app-1", "AWS_SECRET_KEY").allowed is False


class TestSecretPolicy:
    def test_allowed_secret(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        assert e.check_secret("app-1", "API_KEY").allowed is True

    def test_denied_secret(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        assert e.check_secret("app-1", "ADMIN_TOKEN").allowed is False


class TestSubprocessPolicy:
    def test_subprocess_denied_by_default(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        assert e.check_subprocess("app-1").allowed is False

    def test_subprocess_allowed_when_enabled(self):
        e = AppSandboxPolicyEngine()
        p = _app_policy()
        p.allow_subprocess = True
        e.register_app_policy(p)
        assert e.check_subprocess("app-1").allowed is True


class TestPolicyComposition:
    def test_org_override_restricts_env(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        override = SandboxPolicy(
            app_id="app-1",
            allowed_env_vars=["NODE_ENV"],  # restrict from 3 to 1
            max_execution_seconds=30,
            max_memory_mb=128,
        )
        e.set_org_override("app-1", "org-1", override)
        effective = e.get_effective_policy("app-1", "org-1")
        # Only NODE_ENV survives (intersection)
        assert "NODE_ENV" in effective.allowed_env_vars
        assert "API_URL" not in effective.allowed_env_vars

    def test_org_override_restricts_memory(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        override = SandboxPolicy(app_id="app-1", max_execution_seconds=15, max_memory_mb=64)
        e.set_org_override("app-1", "org-1", override)
        effective = e.get_effective_policy("app-1", "org-1")
        assert effective.max_memory_mb == 64   # min of 256 and 64
        assert effective.max_execution_seconds == 15

    def test_composed_always_default_deny_network(self):
        e = AppSandboxPolicyEngine()
        p = _app_policy()
        p.network_default = PolicyAction.ALLOW
        e.register_app_policy(p)
        override = SandboxPolicy(app_id="app-1", max_execution_seconds=60, max_memory_mb=256)
        e.set_org_override("app-1", "org-1", override)
        effective = e.get_effective_policy("app-1", "org-1")
        assert effective.network_default == PolicyAction.DENY

    def test_subprocess_both_must_allow(self):
        e = AppSandboxPolicyEngine()
        p = _app_policy()
        p.allow_subprocess = True
        e.register_app_policy(p)
        override = SandboxPolicy(app_id="app-1", allow_subprocess=False,
                                  max_execution_seconds=60, max_memory_mb=256)
        e.set_org_override("app-1", "org-1", override)
        assert e.check_subprocess("app-1", "org-1").allowed is False

    def test_no_org_override_uses_app_policy(self):
        e = AppSandboxPolicyEngine()
        e.register_app_policy(_app_policy())
        effective = e.get_effective_policy("app-1", "org-1")
        assert effective.max_memory_mb == 256  # app policy, no override
