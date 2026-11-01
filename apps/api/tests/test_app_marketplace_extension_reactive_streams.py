from app.services.app_marketplace_extension_reactive_streams import ReactiveStreamsService


def test_map():
    svc = ReactiveStreamsService()
    result = svc.from_list([1, 2, 3]).map(lambda x: x * 2).collect()
    assert result == [2, 4, 6]


def test_filter():
    svc = ReactiveStreamsService()
    result = svc.from_list([1, 2, 3, 4, 5]).filter(lambda x: x > 3).collect()
    assert result == [4, 5]


def test_chaining():
    svc = ReactiveStreamsService()
    result = (svc.from_range(1, 11)
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x ** 2)
              .collect())
    assert result == [4, 16, 36, 64, 100]


def test_take_skip():
    svc = ReactiveStreamsService()
    result = svc.from_range(0, 10).skip(3).take(4).collect()
    assert result == [3, 4, 5, 6]


def test_distinct():
    svc = ReactiveStreamsService()
    result = svc.from_list([1, 2, 2, 3, 1, 4, 3]).distinct().collect()
    assert result == [1, 2, 3, 4]


def test_flat_map():
    svc = ReactiveStreamsService()
    result = svc.from_list(["hello world", "foo bar"]).flat_map(lambda x: x.split()).collect()
    assert result == ["hello", "world", "foo", "bar"]


def test_batch():
    svc = ReactiveStreamsService()
    result = svc.from_range(1, 8).batch(3).collect()
    assert result == [[1, 2, 3], [4, 5, 6], [7]]


def test_reduce():
    svc = ReactiveStreamsService()
    result = svc.from_list([1, 2, 3, 4]).reduce(lambda a, b: a + b)
    assert result == 10


def test_reduce_with_initial():
    svc = ReactiveStreamsService()
    result = svc.from_list([1, 2, 3]).reduce(lambda a, b: a + b, initial=100)
    assert result == 106


def test_count():
    svc = ReactiveStreamsService()
    assert svc.from_range(0, 100).filter(lambda x: x % 7 == 0).count() == 15


def test_first():
    svc = ReactiveStreamsService()
    assert svc.from_list([10, 20, 30]).first() == 10
    assert svc.empty().first() is None


def test_for_each():
    svc = ReactiveStreamsService()
    collected = []
    svc.from_list([1, 2, 3]).for_each(lambda x: collected.append(x))
    assert collected == [1, 2, 3]


def test_complex_pipeline():
    svc = ReactiveStreamsService()
    # Find sum of squares of odd numbers from 1-20
    result = (svc.from_range(1, 21)
              .filter(lambda x: x % 2 == 1)
              .map(lambda x: x ** 2)
              .reduce(lambda a, b: a + b))
    assert result == 1 + 9 + 25 + 49 + 81 + 121 + 169 + 225 + 289 + 361
