from app.services.app_marketplace_network_policy import (
    NetworkPolicy, NetworkRule, PolicyAction,
)


def test_allow_rule():
    np = NetworkPolicy()
    np.add_rule("ext-1", NetworkRule("r1", "api.slack.com", [443]))
    assert np.is_allowed("ext-1", "api.slack.com", 443) is True


def test_default_deny():
    np = NetworkPolicy(default_action=PolicyAction.DENY)
    assert np.is_allowed("ext-1", "evil.com") is False


def test_wildcard_domain():
    np = NetworkPolicy()
    np.add_rule("ext-2", NetworkRule("r2", "*.github.com", [443]))
    assert np.is_allowed("ext-2", "api.github.com") is True
    assert np.is_allowed("ext-2", "raw.github.com") is True
    assert np.is_allowed("ext-2", "github.com") is False  # no subdomain


def test_port_restriction():
    np = NetworkPolicy()
    np.add_rule("ext-3", NetworkRule("r3", "api.test.com", [443]))
    assert np.is_allowed("ext-3", "api.test.com", 443) is True
    assert np.is_allowed("ext-3", "api.test.com", 8080) is False


def test_deny_rule():
    np = NetworkPolicy(default_action=PolicyAction.ALLOW)
    np.add_rule("ext-4", NetworkRule("r4", "blocked.com", [443], PolicyAction.DENY))
    assert np.is_allowed("ext-4", "blocked.com") is False
    assert np.is_allowed("ext-4", "other.com") is True  # default allow


def test_log_action():
    np = NetworkPolicy()
    np.add_rule("ext-5", NetworkRule("r5", "logged.com", [443], PolicyAction.LOG))
    assert np.is_allowed("ext-5", "logged.com") is True  # log = allow
    log = np.get_access_log("ext-5")
    assert log[0]["action"] == "log"


def test_remove_rule():
    np = NetworkPolicy()
    np.add_rule("ext-6", NetworkRule("r6", "temp.com", [443]))
    assert np.remove_rule("ext-6", "r6") is True
    assert np.is_allowed("ext-6", "temp.com") is False  # rule removed
