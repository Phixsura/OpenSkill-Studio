from app.services.app_marketplace_extension_compression import CompressionEngineService


def test_rle_encode_decode():
    ce = CompressionEngineService()
    data = ["a", "a", "a", "b", "b", "c", "c", "c", "c"]
    result = ce.rle_encode(data)
    assert result.data == [("a", 3), ("b", 2), ("c", 4)]
    assert ce.rle_decode(result.data) == data


def test_rle_single_elements():
    ce = CompressionEngineService()
    data = [1, 2, 3, 4, 5]
    result = ce.rle_encode(data)
    assert ce.rle_decode(result.data) == data


def test_rle_all_same():
    ce = CompressionEngineService()
    data = ["x"] * 100
    result = ce.rle_encode(data)
    assert len(result.data) == 1
    assert result.ratio > 10  # excellent compression


def test_dict_encode_decode():
    ce = CompressionEngineService()
    strings = ["hello", "world", "hello", "hello", "world", "foo"]
    result = ce.dict_encode(strings)
    decoded = ce.dict_decode(result.data)
    assert decoded == strings


def test_dict_many_repeats():
    ce = CompressionEngineService()
    strings = ["very_long_string_that_repeats"] * 50 + ["another_long_one"] * 30
    result = ce.dict_encode(strings)
    assert result.savings_pct > 0
    assert ce.dict_decode(result.data) == strings


def test_delta_encode_decode():
    ce = CompressionEngineService()
    values = [100, 102, 105, 103, 110]
    result = ce.delta_encode(values)
    assert result.data == [100, 2, 3, -2, 7]
    assert ce.delta_decode(result.data) == values


def test_delta_monotonic():
    ce = CompressionEngineService()
    # Monotonically increasing timestamps — excellent for delta
    values = [1000000 + i * 60 for i in range(100)]
    result = ce.delta_encode(values)
    # All deltas are 60 (small) vs original values (large)
    assert result.ratio > 1
    assert ce.delta_decode(result.data) == values


def test_auto_select_repetitive():
    ce = CompressionEngineService()
    data = ["x"] * 100
    result = ce.auto_select(data)
    assert result.algorithm in ("rle", "dictionary")
    assert result.ratio > 5


def test_auto_select_integers():
    ce = CompressionEngineService()
    data = [1000000 + i for i in range(50)]
    result = ce.auto_select(data)
    assert result.algorithm in ("rle", "delta")


def test_empty_data():
    ce = CompressionEngineService()
    assert ce.rle_encode([]).data == []
    assert ce.delta_encode([]).data == []
    assert ce.rle_decode([]) == []
    assert ce.delta_decode([]) == []


def test_compression_metrics():
    ce = CompressionEngineService()
    data = ["a"] * 1000
    result = ce.rle_encode(data)
    assert result.original_size == 1000
    assert result.compressed_size == 2
    assert result.ratio == 500.0
    assert result.savings_pct > 99
