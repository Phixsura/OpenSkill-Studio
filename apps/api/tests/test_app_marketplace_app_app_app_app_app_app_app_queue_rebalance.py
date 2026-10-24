from app.services.app_marketplace_app_app_app_app_app_app_app_queue_rebalance import rebalance_queues

def test_balanced():
    r = rebalance_queues({"high": 50, "normal": 50}, {"high": 0.5, "normal": 0.5})
    assert not r["rebalance_needed"]

def test_imbalanced():
    r = rebalance_queues({"high": 90, "normal": 10}, {"high": 0.5, "normal": 0.5})
    assert r["rebalance_needed"]
    assert r["adjustments"]["high"]["action"] == "decrease"
    assert r["adjustments"]["normal"]["action"] == "increase"
