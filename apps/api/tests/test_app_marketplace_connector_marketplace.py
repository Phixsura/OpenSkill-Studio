from app.services.app_marketplace_connector_marketplace import (
    publish_connector, install_connector, uninstall_connector,
    list_connectors, get_org_connectors, rate_connector,
)


def test_publish_and_list():
    publish_connector("slack-001", "Slack Notifier", "SlackCorp", "messaging", "1.0.0")
    publish_connector("gh-001", "GitHub Sync", "GitHubInc", "scm", "2.1.0")
    all_c = list_connectors()
    assert len(all_c) >= 2
    messaging = list_connectors(category="messaging")
    assert all(c["category"] == "messaging" for c in messaging)


def test_install_and_uninstall():
    publish_connector("jira-001", "Jira Tracker", "Atlassian", "pm", "3.0.0")
    result = install_connector("org-100", "jira-001")
    assert result is not None
    assert result["installed"] is True
    org_conns = get_org_connectors("org-100")
    assert any(c["connector_id"] == "jira-001" for c in org_conns)
    removed = uninstall_connector("org-100", "jira-001")
    assert removed is True


def test_install_nonexistent():
    result = install_connector("org-200", "nonexistent-connector")
    assert result is None


def test_rate_connector():
    publish_connector("rate-001", "Rated Plugin", "RateCo", "analytics", "1.0.0")
    rate_connector("rate-001", 5.0)
    rate_connector("rate-001", 3.0)
    connector = rate_connector("rate-001", 4.0)
    assert connector is not None
    assert connector["reviews"] == 3
    assert 3.5 <= connector["rating"] <= 4.5


def test_duplicate_install():
    publish_connector("dup-001", "Dup Plugin", "DupCo", "tools", "1.0.0")
    install_connector("org-300", "dup-001")
    install_connector("org-300", "dup-001")  # duplicate
    org_conns = get_org_connectors("org-300")
    dup_count = sum(1 for c in org_conns if c["connector_id"] == "dup-001")
    assert dup_count == 1
