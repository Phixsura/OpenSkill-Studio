from app.services.app_marketplace_app_env_config import build_env_config
def test_config():
    r = build_env_config(env_vars={"PORT": "3000", "DB_PASS": "secret123"}, secrets=["DB_PASS"])
    assert r["total"] == 2
    assert r["secret_count"] == 1
    assert r["variables"][1]["value"] == "••••••"
