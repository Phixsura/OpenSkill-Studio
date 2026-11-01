from app.services.app_marketplace_app_app_app_app_app_app_app_tx_coordinator import begin_transaction, vote, tx_summary

def test_commit():
    tx = begin_transaction(["order", "payment", "inventory"])
    vote(tx, "order", True)
    vote(tx, "payment", True)
    r = vote(tx, "inventory", True)
    assert r["tx_status"] == "committed"

def test_abort():
    tx = begin_transaction(["a", "b"])
    vote(tx, "a", True)
    r = vote(tx, "b", False)
    assert r["tx_status"] == "aborted"

def test_summary():
    txs = [{"status": "committed"}, {"status": "committed"}, {"status": "aborted"}]
    r = tx_summary(txs)
    assert r["success_rate"] == 67
