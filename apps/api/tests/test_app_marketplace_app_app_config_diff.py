from app.services.app_marketplace_app_app_config_diff import compare_environments

def test_compare():
    envs = {
        "dev": {"PORT": "3000", "DEBUG": "true", "DB_HOST": "localhost"},
        "staging": {"PORT": "3000", "DEBUG": "false", "DB_HOST": "staging-db"},
        "prod": {"PORT": "3000", "DEBUG": "false", "DB_HOST": "prod-db", "CDN": "https://cdn.example.com"},
    }
    r = compare_environments(envs=envs)
    assert r["total_keys"] == 4
    assert r["environments"] == ["dev", "staging", "prod"]
    assert not r["in_sync"]
    assert r["mismatches"] >= 3  # DEBUG differs, DB_HOST differs, CDN missing in dev/staging

def test_in_sync():
    r = compare_environments(envs={"a": {"X": "1"}, "b": {"X": "1"}})
    assert r["in_sync"]
