from app.services.app_manifest_normalizer import normalize_manifest, manifests_equal

def test_sorts_permissions():
    m = normalize_manifest({"permissions": ["write:cohorts", "read:cohorts"]})
    assert m["permissions"] == ["read:cohorts", "write:cohorts"]

def test_sorts_events():
    m = normalize_manifest({"event_subscriptions": ["b.event", "a.event"]})
    assert m["event_subscriptions"] == ["a.event", "b.event"]

def test_sorts_secrets():
    m = normalize_manifest({"secrets": [{"key": "B"}, {"key": "A"}]})
    assert m["secrets"][0]["key"] == "A"

def test_normalizes_hosts():
    m = normalize_manifest({"sandbox": {"network": {"allowed_hosts": ["B.COM", "a.com"]}}})
    assert m["sandbox"]["network"]["allowed_hosts"] == ["a.com", "b.com"]

def test_equal_different_order():
    a = {"permissions": ["write:x", "read:x"]}
    b = {"permissions": ["read:x", "write:x"]}
    assert manifests_equal(a, b) is True

def test_not_equal():
    a = {"permissions": ["read:x"]}
    b = {"permissions": ["write:x"]}
    assert manifests_equal(a, b) is False

def test_no_mutation():
    original = {"permissions": ["b", "a"]}
    normalize_manifest(original)
    assert original["permissions"] == ["b", "a"]
