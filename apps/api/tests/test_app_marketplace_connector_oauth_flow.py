from app.services.app_marketplace_connector_oauth_flow import ConnectorOAuthFlow


def test_initiate():
    flow = ConnectorOAuthFlow()
    result = flow.initiate("slack-conn", "org-1", "slack", ["channels:read"], "https://app.com/cb")
    assert "auth_url" in result
    assert "slack.com" in result["auth_url"]
    assert "state" in result


def test_complete_flow():
    flow = ConnectorOAuthFlow()
    init = flow.initiate("gh-conn", "org-1", "github", ["repo"], "https://app.com/cb")
    conn, msg = flow.complete(init["state"], "auth_code_123")
    assert conn is not None
    assert conn.status == "connected"
    assert conn.provider == "github"
    assert msg == "Connected"


def test_invalid_state():
    flow = ConnectorOAuthFlow()
    conn, msg = flow.complete("bogus_state", "code")
    assert conn is None
    assert "Invalid" in msg


def test_refresh():
    flow = ConnectorOAuthFlow()
    init = flow.initiate("conn", "org-1", "slack", ["read"], "https://cb.com")
    conn, _ = flow.complete(init["state"], "code123")
    ok, msg = flow.refresh(conn.connection_id)
    assert ok is True
    assert flow.get_connection(conn.connection_id).last_refreshed != ""


def test_revoke():
    flow = ConnectorOAuthFlow()
    init = flow.initiate("conn", "org-1", "slack", ["read"], "https://cb.com")
    conn, _ = flow.complete(init["state"], "code")
    assert flow.revoke(conn.connection_id) is True
    assert flow.get_connection(conn.connection_id).status == "revoked"


def test_cannot_refresh_revoked():
    flow = ConnectorOAuthFlow()
    init = flow.initiate("conn", "org-2", "github", ["repo"], "https://cb.com")
    conn, _ = flow.complete(init["state"], "code")
    flow.revoke(conn.connection_id)
    ok, msg = flow.refresh(conn.connection_id)
    assert ok is False
    assert "revoked" in msg


def test_is_connected():
    flow = ConnectorOAuthFlow()
    init = flow.initiate("my-conn", "org-3", "slack", ["read"], "https://cb.com")
    flow.complete(init["state"], "code")
    assert flow.is_connected("org-3", "my-conn") is True
    assert flow.is_connected("org-3", "other-conn") is False


def test_list_connections():
    flow = ConnectorOAuthFlow()
    for i, provider in enumerate(["slack", "github", "slack"]):
        init = flow.initiate(f"c{i}", "org-4", provider, ["read"], "https://cb.com")
        flow.complete(init["state"], f"code{i}")
    all_conns = flow.list_connections("org-4")
    assert len(all_conns) == 3
    slack_conns = flow.list_connections("org-4", provider="slack")
    assert len(slack_conns) == 2
