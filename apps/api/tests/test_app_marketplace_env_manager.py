from app.services.app_marketplace_env_manager import EnvironmentManager


def test_set_and_get():
    em = EnvironmentManager()
    ok, _ = em.set_var("ext-1", "API_URL", "https://api.test.com")
    assert ok
    var = em.get_var("ext-1", "API_URL")
    assert var is not None
    assert var.value == "https://api.test.com"


def test_reserved_prefix_rejected():
    em = EnvironmentManager()
    ok, err = em.set_var("ext-2", "OPENSKILL_SECRET", "nope")
    assert ok is False
    assert "reserved" in err


def test_encrypted_masking():
    em = EnvironmentManager()
    em.set_var("ext-3", "DB_PASS", "s3cret", encrypted=True)
    listed = em.list_vars("ext-3", mask_encrypted=True)
    assert listed[0]["value"] == "***"
    unmasked = em.list_vars("ext-3", mask_encrypted=False)
    assert unmasked[0]["value"] == "s3cret"


def test_org_override():
    em = EnvironmentManager()
    em.set_var("ext-4", "MODE", "production")
    em.set_var("ext-4", "MODE", "staging", org_id="org-1")
    env = em.get_runtime_env("ext-4", "org-1")
    assert env["MODE"] == "staging"  # org overrides extension


def test_delete():
    em = EnvironmentManager()
    em.set_var("ext-5", "TEMP", "val")
    assert em.delete_var("ext-5", "TEMP") is True
    assert em.get_var("ext-5", "TEMP") is None


def test_invalid_key():
    em = EnvironmentManager()
    ok, _ = em.set_var("ext-6", "bad key!", "val")
    assert ok is False


def test_runtime_env_merge():
    em = EnvironmentManager()
    em.set_var("ext-7", "A", "1")
    em.set_var("ext-7", "B", "2")
    em.set_var("ext-7", "A", "override", org_id="org-x")
    env = em.get_runtime_env("ext-7", "org-x")
    assert env == {"A": "override", "B": "2"}
