from app.services.app_marketplace_app_app_app_app_app_app_app_key_rotation import KeyRotationScheduler

def test_register():
    krs = KeyRotationScheduler(rotation_days=90)
    r = krs.register_key("db-password", created_days_ago=100)
    assert r["overdue"]
    assert r["due_in_days"] == 0

def test_rotate():
    krs = KeyRotationScheduler(rotation_days=90)
    krs.register_key("api-key", created_days_ago=100)
    krs.rotate("api-key")
    assert krs._keys["api-key"]["age_days"] == 0
    assert len(krs.overdue_keys()) == 0

def test_stats():
    krs = KeyRotationScheduler(rotation_days=30)
    krs.register_key("k1", created_days_ago=50)
    krs.register_key("k2", created_days_ago=10)
    s = krs.stats()
    assert s["overdue"] == 1
    assert s["total_keys"] == 2
