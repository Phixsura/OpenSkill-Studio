from app.services.app_marketplace_extension_playground_executor import PlaygroundExecutor


def test_simple_execution():
    pe = PlaygroundExecutor()
    result = pe.execute("ext-1", "print('hello')\nprint('world')")
    assert result.success is True
    assert "hello" in result.stdout
    assert "world" in result.stdout
    assert result.duration_ms > 0


def test_empty_code():
    pe = PlaygroundExecutor()
    result = pe.execute("ext-2", "")
    assert result.success is False
    assert result.error_type == "EmptyCode"


def test_large_code():
    pe = PlaygroundExecutor()
    result = pe.execute("ext-3", "x = 1\n" * 200000)
    assert result.success is False
    assert result.error_type == "SizeLimit"


def test_assignment():
    pe = PlaygroundExecutor()
    result = pe.execute("ext-4", "x = 42")
    assert result.success is True
    assert result.return_value == "42"


def test_history():
    pe = PlaygroundExecutor()
    pe.execute("ext-5", "print('a')")
    pe.execute("ext-5", "print('b')")
    pe.execute("ext-5", "print('c')")
    history = pe.get_history("ext-5")
    assert len(history) == 3


def test_stats():
    pe = PlaygroundExecutor()
    pe.execute("ext-6", "print('ok')")
    pe.execute("ext-6", "print('ok')")
    pe.execute("ext-6", "")
    stats = pe.get_stats("ext-6")
    assert stats["executions"] == 3
    assert stats["success_rate"] < 100  # one failure


def test_clear_history():
    pe = PlaygroundExecutor()
    pe.execute("ext-7", "x = 1")
    assert pe.clear_history("ext-7") == 1
    assert pe.get_history("ext-7") == []
