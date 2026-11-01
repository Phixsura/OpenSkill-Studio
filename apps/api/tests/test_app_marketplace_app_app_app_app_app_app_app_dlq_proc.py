from app.services.app_marketplace_app_app_app_app_app_app_app_dlq_proc import DlqProcessor

def test_add_reprocess():
    dlq = DlqProcessor()
    dlq.add("m1", {"data": "x"}, "timeout", 3)
    dlq.add("m2", {"data": "y"}, "500 error", 5)
    dlq.reprocess("m1")
    assert dlq.stats()["pending"] == 1
    assert dlq.stats()["reprocessed"] == 1

def test_discard():
    dlq = DlqProcessor()
    dlq.add("m1", {}, "fatal", 10)
    dlq.discard("m1")
    assert dlq.stats()["discarded"] == 1
    assert dlq.stats()["pending"] == 0
