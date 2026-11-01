from app.services.app_marketplace_extension_request_router import (
    RequestRouterService, RouteRule, RouteTarget
)


def test_simple_route():
    router = RequestRouterService()
    router.add_rule(RouteRule(rule_id="api",
                              match_path=r"^/api/",
                              targets=[RouteTarget("api-service")]))
    decision = router.route("GET", "/api/users")
    assert decision.target == "api-service"


def test_method_matching():
    router = RequestRouterService()
    router.add_rule(RouteRule(rule_id="post-only", match_method="POST",
                              match_path=r"^/submit",
                              targets=[RouteTarget("submit-svc")]))
    d1 = router.route("POST", "/submit")
    assert d1.target == "submit-svc"
    d2 = router.route("GET", "/submit")
    assert d2.target == "default"  # no match


def test_header_matching():
    router = RequestRouterService()
    router.add_rule(RouteRule(rule_id="beta", match_headers={"X-Beta": "true"},
                              targets=[RouteTarget("beta-service")]))
    d1 = router.route("GET", "/app", headers={"X-Beta": "true"})
    assert d1.target == "beta-service"
    d2 = router.route("GET", "/app", headers={})
    assert d2.target == "default"


def test_weighted_split():
    router = RequestRouterService()
    router.add_rule(RouteRule(rule_id="canary", match_path=r"^/",
                              targets=[RouteTarget("stable", weight=90),
                                       RouteTarget("canary", weight=10)]))
    targets = set()
    for i in range(200):
        d = router.route("GET", "/page", routing_key=f"user-{i}")
        targets.add(d.target)
    assert "stable" in targets
    assert "canary" in targets


def test_mirror():
    router = RequestRouterService()
    router.add_rule(RouteRule(rule_id="prod", match_path=r"^/api/",
                              targets=[RouteTarget("prod-svc"),
                                       RouteTarget("shadow-svc", mirror=True)]))
    d = router.route("GET", "/api/data")
    assert d.target == "prod-svc"
    assert "shadow-svc" in d.mirrors


def test_priority():
    router = RequestRouterService()
    router.add_rule(RouteRule(rule_id="specific", priority=10,
                              match_path=r"^/api/admin",
                              targets=[RouteTarget("admin-svc")]))
    router.add_rule(RouteRule(rule_id="general", priority=1,
                              match_path=r"^/api/",
                              targets=[RouteTarget("api-svc")]))
    d = router.route("GET", "/api/admin/users")
    assert d.target == "admin-svc"


def test_fallback():
    router = RequestRouterService()
    router.add_rule(RouteRule(rule_id="r1", match_path=r"^/api/",
                              targets=[], fallback="fallback-svc"))
    d = router.route("GET", "/api/data")
    assert d.target == "fallback-svc"


def test_default_route():
    router = RequestRouterService()
    router.set_default("catch-all")
    d = router.route("GET", "/unknown/path")
    assert d.target == "catch-all"


def test_regex_header():
    router = RequestRouterService()
    router.add_rule(RouteRule(rule_id="tenant",
                              match_headers={"X-Tenant": "regex:^(acme|globex)$"},
                              targets=[RouteTarget("multi-tenant-svc")]))
    d1 = router.route("GET", "/", headers={"X-Tenant": "acme"})
    assert d1.target == "multi-tenant-svc"
    d2 = router.route("GET", "/", headers={"X-Tenant": "unknown"})
    assert d2.target == "default"
