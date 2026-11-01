from app.services.app_marketplace_extension_trie_router import TrieRouterService


def test_static_route():
    r = TrieRouterService()
    r.add("GET", "/api/users", "list_users")
    m = r.match("GET", "/api/users")
    assert m is not None
    assert m.handler == "list_users"
    assert m.params == {}


def test_param_route():
    r = TrieRouterService()
    r.add("GET", "/api/users/:id", "get_user")
    m = r.match("GET", "/api/users/42")
    assert m is not None
    assert m.handler == "get_user"
    assert m.params == {"id": "42"}


def test_multiple_params():
    r = TrieRouterService()
    r.add("GET", "/api/orgs/:org_id/repos/:repo_id", "get_repo")
    m = r.match("GET", "/api/orgs/acme/repos/widget")
    assert m is not None
    assert m.params == {"org_id": "acme", "repo_id": "widget"}


def test_wildcard_route():
    r = TrieRouterService()
    r.add("GET", "/static/*filepath", "serve_file")
    m = r.match("GET", "/static/css/main.css")
    assert m is not None
    assert m.params == {"filepath": "css/main.css"}


def test_method_routing():
    r = TrieRouterService()
    r.add("GET", "/api/items", "list_items")
    r.add("POST", "/api/items", "create_item")
    get_m = r.match("GET", "/api/items")
    post_m = r.match("POST", "/api/items")
    assert get_m.handler == "list_items"
    assert post_m.handler == "create_item"
    # Wrong method
    assert r.match("DELETE", "/api/items") is None


def test_static_over_param_priority():
    r = TrieRouterService()
    r.add("GET", "/api/users/me", "get_me")
    r.add("GET", "/api/users/:id", "get_user")
    # /me should match static route, not param
    m = r.match("GET", "/api/users/me")
    assert m.handler == "get_me"
    # Other values match param
    m2 = r.match("GET", "/api/users/42")
    assert m2.handler == "get_user"


def test_no_match():
    r = TrieRouterService()
    r.add("GET", "/api/users", "list")
    assert r.match("GET", "/api/posts") is None
    assert r.match("GET", "/api/users/1/extra") is None


def test_conflict_detection():
    r = TrieRouterService()
    r.add("GET", "/api/data", "handler1")
    try:
        r.add("GET", "/api/data", "handler2")
        assert False
    except ValueError:
        pass


def test_middleware():
    r = TrieRouterService()
    r.add("GET", "/admin/users", "admin_users", middleware=["auth", "admin_check"])
    m = r.match("GET", "/admin/users")
    assert m.middleware == ["auth", "admin_check"]


def test_route_count():
    r = TrieRouterService()
    r.add("GET", "/a", "ha")
    r.add("POST", "/b", "hb")
    r.add("GET", "/c/:id", "hc")
    assert r.route_count() == 3
