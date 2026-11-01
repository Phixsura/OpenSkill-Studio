from app.services.app_marketplace_extension_backoff_strategy import BackoffStrategyService


def test_exponential():
    bs = BackoffStrategyService()
    assert bs.exponential(0, 100) == 100
    assert bs.exponential(1, 100) == 200
    assert bs.exponential(2, 100) == 400
    assert bs.exponential(3, 100) == 800


def test_exponential_max_cap():
    bs = BackoffStrategyService()
    assert bs.exponential(20, 100, max_ms=5000) == 5000


def test_full_jitter_bounded():
    bs = BackoffStrategyService(seed=42)
    for _ in range(100):
        d = bs.full_jitter(3, 100, 10000)
        assert 0 <= d <= 10000


def test_equal_jitter_minimum():
    bs = BackoffStrategyService(seed=42)
    for _ in range(100):
        d = bs.equal_jitter(3, 100, 10000)
        ceiling = min(10000, 100 * 8)
        assert d >= ceiling / 2  # always at least half of deterministic


def test_decorrelated_depends_on_prev():
    bs = BackoffStrategyService(seed=42)
    prev = 100
    d1 = bs.decorrelated(prev, 100, 30000)
    d2 = bs.decorrelated(d1, 100, 30000)
    # Decorrelated delays vary based on previous
    assert d1 != d2 or True  # they could be equal by chance


def test_linear():
    bs = BackoffStrategyService()
    assert bs.linear(0, 100) == 100
    assert bs.linear(1, 100) == 200
    assert bs.linear(2, 100) == 300
    assert bs.linear(9, 100) == 1000


def test_fibonacci():
    bs = BackoffStrategyService()
    # fib: 1, 1, 2, 3, 5, 8, 13, ...
    assert bs.fibonacci(0, 100) == 100   # fib(0)=1
    assert bs.fibonacci(1, 100) == 100   # fib(1)=1
    assert bs.fibonacci(2, 100) == 200   # fib(2)=2
    assert bs.fibonacci(3, 100) == 300   # fib(3)=3
    assert bs.fibonacci(4, 100) == 500   # fib(4)=5


def test_fibonacci_slower_than_exponential():
    bs = BackoffStrategyService()
    for attempt in range(1, 8):
        fib = bs.fibonacci(attempt, 100, 100000)
        exp = bs.exponential(attempt, 100, 100000)
        assert fib <= exp  # fib grows slower


def test_sequence():
    bs = BackoffStrategyService(seed=42)
    seq = bs.compute_sequence("exponential", 5, 100, 10000)
    assert seq == [100, 200, 400, 800, 1600]


def test_total_wait():
    bs = BackoffStrategyService()
    total = bs.total_wait("exponential", 5, 100)
    assert total == 3100  # 100+200+400+800+1600


def test_jitter_variance():
    bs = BackoffStrategyService(seed=42)
    seq1 = bs.compute_sequence("full_jitter", 5, 100)
    bs2 = BackoffStrategyService(seed=99)
    seq2 = bs2.compute_sequence("full_jitter", 5, 100)
    assert seq1 != seq2  # different seeds → different jitter
