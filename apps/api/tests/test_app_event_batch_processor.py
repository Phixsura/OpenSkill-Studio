from app.services.app_event_batch_processor import create_batch, split_batch, merge_batch_results

def test_create_batch():
    b = create_batch([{"event": "a"}, {"event": "b"}])
    assert b["count"] == 2
    assert b["status"] == "pending"
    assert b["batch_id"].startswith("batch_")

def test_split():
    events = [{"id": i} for i in range(120)]
    chunks = split_batch(events, chunk_size=50)
    assert len(chunks) == 3
    assert len(chunks[0]) == 50
    assert len(chunks[2]) == 20

def test_split_small():
    chunks = split_batch([{"id": 1}], chunk_size=50)
    assert len(chunks) == 1

def test_merge():
    results = [{"processed": 50, "failed": 2}, {"processed": 50, "failed": 0}, {"processed": 20, "failed": 1}]
    m = merge_batch_results(results)
    assert m["total_processed"] == 120
    assert m["total_failed"] == 3
    assert m["chunks"] == 3

def test_merge_empty():
    m = merge_batch_results([])
    assert m["total_processed"] == 0
    assert m["success_rate"] == 100.0
