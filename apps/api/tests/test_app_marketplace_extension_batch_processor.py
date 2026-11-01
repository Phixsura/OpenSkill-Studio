from app.services.app_marketplace_extension_batch_processor import BatchProcessorService


def test_basic_batch():
    bp = BatchProcessorService()
    result = bp.process(list(range(10)),
                        lambda chunk: sum(chunk), chunk_size=3)
    assert result.total_items == 10
    assert result.total_chunks == 4  # ceil(10/3)
    assert result.total_processed == 10
    assert result.chunks_failed == 0


def test_chunk_results():
    bp = BatchProcessorService()
    result = bp.process([1, 2, 3, 4, 5],
                        lambda chunk: sum(chunk), chunk_size=2)
    assert result.results[0].result == 3  # 1+2
    assert result.results[1].result == 7  # 3+4
    assert result.results[2].result == 5  # 5


def test_error_handling():
    bp = BatchProcessorService()
    def risky(chunk):
        if any(x == 5 for x in chunk):
            raise ValueError("bad value 5")
        return len(chunk)
    result = bp.process(list(range(10)), risky, chunk_size=3)
    assert result.chunks_failed == 1  # chunk with 5
    assert result.chunks_completed == 3
    assert result.total_errors == 3  # that chunk's items


def test_progress_callback():
    bp = BatchProcessorService()
    progress_log = []
    bp.process(list(range(100)), lambda c: len(c), chunk_size=25,
               on_progress=lambda p: progress_log.append(p))
    assert len(progress_log) == 4
    assert progress_log[-1]["pct"] == 100.0


def test_resume():
    bp = BatchProcessorService()
    # Process from chunk 2 (skipping first 2 chunks)
    result = bp.process(list(range(20)), lambda c: sum(c),
                        chunk_size=5, resume_from=2)
    assert result.chunks_completed == 2  # only chunks 2,3
    assert result.total_processed == 10  # items 10-19


def test_success_rate():
    bp = BatchProcessorService()
    call_count = [0]
    def sometimes_fail(chunk):
        call_count[0] += 1
        if call_count[0] == 2:
            raise RuntimeError("fail")
        return len(chunk)
    result = bp.process(list(range(15)), sometimes_fail, chunk_size=5)
    assert result.success_rate < 100


def test_chunk_list():
    bp = BatchProcessorService()
    chunks = bp.chunk_list(list(range(7)), 3)
    assert chunks == [[0, 1, 2], [3, 4, 5], [6]]


def test_batch_id_tracking():
    bp = BatchProcessorService()
    bp.process(list(range(20)), lambda c: None, chunk_size=5,
               batch_id="job-1")
    progress = bp.get_progress("job-1")
    assert progress["pct"] == 100.0


def test_single_chunk():
    bp = BatchProcessorService()
    result = bp.process([1, 2, 3], lambda c: sum(c), chunk_size=100)
    assert result.total_chunks == 1
    assert result.results[0].result == 6


def test_empty():
    bp = BatchProcessorService()
    result = bp.process([], lambda c: None, chunk_size=10)
    assert result.total_items == 0
    assert result.total_chunks == 0
