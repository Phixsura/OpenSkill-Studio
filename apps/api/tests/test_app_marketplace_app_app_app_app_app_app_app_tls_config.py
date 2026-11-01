from app.services.app_marketplace_app_app_app_app_app_app_app_tls_config import evaluate_tls_config, tls_summary

def test_grade_a():
    r = evaluate_tls_config("1.3", ["TLS_AES_256_GCM_SHA384"])
    assert r["grade"] == "A"
    assert r["secure"]

def test_grade_f():
    r = evaluate_tls_config("1.0", ["TLS_RSA_WITH_AES_128_CBC_SHA"])
    assert r["grade"] == "F"
    assert not r["secure"]

def test_summary():
    configs = [{"secure": True}, {"secure": True}, {"secure": False}]
    r = tls_summary(configs)
    assert r["secure_pct"] == 67
