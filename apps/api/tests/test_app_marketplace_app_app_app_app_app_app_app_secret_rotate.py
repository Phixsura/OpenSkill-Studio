import time
from app.services.app_marketplace_app_app_app_app_app_app_app_secret_rotate import check_rotation, rotation_plan

def test_check():
    now = time.time()
    r = check_rotation([
        {"name": "db_pass", "created_at": now - 86400 * 100, "type": "password"},
        {"name": "api_key", "created_at": now - 86400 * 10, "type": "api_key"},
    ], max_age_days=90)
    assert r["overdue"] == 1
    assert r["healthy"] == 1
    assert r["secrets"][0]["overdue"]
    assert not r["secrets"][1]["overdue"]

def test_plan():
    plan = rotation_plan([
        {"name": "old_key", "age_days": 200},
        {"name": "older_key", "age_days": 300},
    ])
    assert plan[0]["name"] == "older_key"
    assert plan[0]["priority"] == 1
