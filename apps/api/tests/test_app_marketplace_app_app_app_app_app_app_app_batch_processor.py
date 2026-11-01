from app.services.app_marketplace_app_app_app_app_app_app_app_batch_processor import BatchProcessor

def test_batch():
    bp = BatchProcessor(list(range(250)), batch_size=100)
    assert bp.total_batches() == 3
    bp.process_batch(0)
    bp.process_batch(1, success_rate=0.9)
    bp.process_batch(2)
    p = bp.progress()
    assert p["processed"] == 240  # 100 + 90 + 50
    assert p["failed"] == 10
    assert p["status"] == "completed"
    assert p["progress_pct"] == 100.0
