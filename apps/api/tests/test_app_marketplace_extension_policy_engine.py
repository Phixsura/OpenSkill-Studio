from app.services.app_marketplace_extension_policy_engine import (
    PolicyEngineService, Policy, PolicyCondition, AccessRequest, Effect
)


def test_simple_allow():
    engine = PolicyEngineService()
    engine.add_policy(Policy("p1", "Allow admins", effect=Effect.ALLOW, conditions=[
        PolicyCondition("subject", "role", "eq", "admin"),
    ]))
    decision = engine.evaluate(AccessRequest(
        subject={"role": "admin"}, resource={"type": "document"}, action="read"))
    assert decision.effect == Effect.ALLOW


def test_default_deny():
    engine = PolicyEngineService(default_effect=Effect.DENY)
    decision = engine.evaluate(AccessRequest(
        subject={"role": "guest"}, resource={}, action="read"))
    assert decision.effect == Effect.DENY
    assert "No matching" in decision.reason


def test_deny_overrides_allow():
    engine = PolicyEngineService()
    engine.add_policy(Policy("allow", "Allow employees", effect=Effect.ALLOW, conditions=[
        PolicyCondition("subject", "role", "eq", "employee"),
    ]))
    engine.add_policy(Policy("deny", "Deny classified", effect=Effect.DENY, conditions=[
        PolicyCondition("resource", "classification", "eq", "secret"),
    ]))
    decision = engine.evaluate(AccessRequest(
        subject={"role": "employee"},
        resource={"classification": "secret"}, action="read"))
    assert decision.effect == Effect.DENY


def test_multi_condition():
    engine = PolicyEngineService()
    engine.add_policy(Policy("p1", "Department access", effect=Effect.ALLOW, conditions=[
        PolicyCondition("subject", "department", "eq", "engineering"),
        PolicyCondition("resource", "type", "eq", "code"),
        PolicyCondition("action", "type", "in", ["read", "write"]),
    ]))
    decision = engine.evaluate(AccessRequest(
        subject={"department": "engineering"},
        resource={"type": "code"}, action="read"))
    assert decision.effect == Effect.ALLOW
    # Wrong department
    decision2 = engine.evaluate(AccessRequest(
        subject={"department": "marketing"},
        resource={"type": "code"}, action="read"))
    assert decision2.effect == Effect.DENY


def test_environment_conditions():
    engine = PolicyEngineService()
    engine.add_policy(Policy("p1", "Office hours only", effect=Effect.ALLOW, conditions=[
        PolicyCondition("subject", "role", "eq", "employee"),
        PolicyCondition("environment", "hour", "gt", 8),
        PolicyCondition("environment", "hour", "lt", 18),
    ]))
    # During work hours
    d1 = engine.evaluate(AccessRequest(
        subject={"role": "employee"}, resource={}, action="read",
        environment={"hour": 10}))
    assert d1.effect == Effect.ALLOW
    # After hours
    d2 = engine.evaluate(AccessRequest(
        subject={"role": "employee"}, resource={}, action="read",
        environment={"hour": 22}))
    assert d2.effect == Effect.DENY


def test_obligations():
    engine = PolicyEngineService()
    engine.add_policy(Policy("p1", "Allow with logging", effect=Effect.ALLOW,
                             conditions=[PolicyCondition("subject", "role", "eq", "auditor")],
                             obligations=["log_access", "notify_owner"]))
    decision = engine.evaluate(AccessRequest(
        subject={"role": "auditor"}, resource={}, action="read"))
    assert decision.effect == Effect.ALLOW
    assert "log_access" in decision.obligations


def test_regex_matching():
    engine = PolicyEngineService()
    engine.add_policy(Policy("p1", "API path match", effect=Effect.ALLOW, conditions=[
        PolicyCondition("resource", "path", "matches", r"^/api/v[12]/"),
    ]))
    d1 = engine.evaluate(AccessRequest(
        subject={}, resource={"path": "/api/v1/users"}, action="read"))
    assert d1.effect == Effect.ALLOW
    d2 = engine.evaluate(AccessRequest(
        subject={}, resource={"path": "/admin/panel"}, action="read"))
    assert d2.effect == Effect.DENY


def test_priority():
    engine = PolicyEngineService()
    engine.add_policy(Policy("low", "General allow", effect=Effect.ALLOW, priority=1,
                             conditions=[PolicyCondition("action", "type", "eq", "read")]))
    engine.add_policy(Policy("high", "VIP allow", effect=Effect.ALLOW, priority=10,
                             conditions=[PolicyCondition("action", "type", "eq", "read")],
                             obligations=["vip_treatment"]))
    decision = engine.evaluate(AccessRequest(subject={}, resource={}, action="read"))
    assert decision.matched_policy == "high"
    assert "vip_treatment" in decision.obligations


def test_disabled_policy():
    engine = PolicyEngineService()
    engine.add_policy(Policy("p1", "Disabled", effect=Effect.ALLOW, enabled=False,
                             conditions=[PolicyCondition("action", "type", "eq", "read")]))
    decision = engine.evaluate(AccessRequest(subject={}, resource={}, action="read"))
    assert decision.effect == Effect.DENY  # default deny, disabled policy skipped
