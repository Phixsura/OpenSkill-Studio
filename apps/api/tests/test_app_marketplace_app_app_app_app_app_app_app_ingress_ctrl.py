from app.services.app_marketplace_app_app_app_app_app_app_app_ingress_ctrl import IngressController

def test_routing():
    ic = IngressController()
    ic.add_rule("api.example.com", "/v1", "api-svc")
    ic.add_rule("app.example.com", "/", "web-svc")
    r = ic.match("api.example.com", "/v1/users")
    assert r["matched"]
    assert r["backend"] == "api-svc"

def test_expiring_certs():
    ic = IngressController()
    ic.add_cert("api.example.com", "letsencrypt", 10)
    ic.add_cert("app.example.com", "letsencrypt", 90)
    exp = ic.expiring_certs(within_days=30)
    assert len(exp) == 1
    assert exp[0]["domain"] == "api.example.com"
