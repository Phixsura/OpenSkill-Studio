from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_retry_budget import MeshRetryBudget

def test_budget():
    mrb = MeshRetryBudget(budget_pct=20)
    for _ in range(100):
        mrb.record_request("api", "db")
    for _ in range(15):
        mrb.record_request("api", "db", is_retry=True)
    r = mrb.check_budget("api", "db")
    assert r["budget"] == 20  # 20% of 100
    assert r["used"] == 15
    assert r["can_retry"]

def test_exhausted():
    mrb = MeshRetryBudget(budget_pct=10)
    for _ in range(10):
        mrb.record_request("a", "b")
    for _ in range(1):
        mrb.record_request("a", "b", is_retry=True)
    r = mrb.check_budget("a", "b")
    assert r["budget"] == 1
    assert r["exhausted"]
