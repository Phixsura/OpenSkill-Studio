from app.services.app_webhook_backoff import compute_backoff, compute_schedule, total_delay

def test_increases():
    d0 = compute_backoff(0, jitter=False)
    d1 = compute_backoff(1, jitter=False)
    d2 = compute_backoff(2, jitter=False)
    assert d1 > d0 and d2 > d1

def test_capped():
    d = compute_backoff(100, jitter=False, max_seconds=3600)
    assert d <= 3600

def test_jitter_varies():
    delays = {compute_backoff(3) for _ in range(20)}
    assert len(delays) > 1

def test_schedule_length():
    assert len(compute_schedule(5)) == 5

def test_total_delay():
    t = total_delay(5, base_seconds=10)
    assert t > 0 and t < 100000
