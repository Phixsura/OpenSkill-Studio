from app.services.app_marketplace_extension_stream_processor import StreamProcessorService


def test_tumbling_window():
    sp = StreamProcessorService()
    for i in range(10):
        sp.emit("sensor", float(i), timestamp=100.0 + i)
    windows = sp.tumbling_window(5.0, "sensor")
    assert len(windows) == 2  # [100-105), [105-110)
    assert windows[0].count == 5
    assert windows[1].count == 5


def test_tumbling_aggregation():
    sp = StreamProcessorService()
    sp.emit("m", 10.0, 100.0)
    sp.emit("m", 20.0, 101.0)
    sp.emit("m", 30.0, 102.0)
    windows = sp.tumbling_window(5.0, "m")
    assert windows[0].avg == 20.0
    assert windows[0].min_val == 10.0
    assert windows[0].max_val == 30.0
    assert windows[0].total == 60.0


def test_sliding_window():
    sp = StreamProcessorService()
    for i in range(10):
        sp.emit("s", 1.0, timestamp=100.0 + i)
    windows = sp.sliding_window(5.0, 2.0, "s")
    # Sliding windows overlap — more results than tumbling
    assert len(windows) > 2
    # Each window should have up to 5 events
    assert all(w.count <= 5 for w in windows)


def test_session_window():
    sp = StreamProcessorService()
    # Session 1: events at 100-103
    sp.emit("user", 1.0, 100.0)
    sp.emit("user", 1.0, 101.0)
    sp.emit("user", 1.0, 103.0)
    # Gap > 5
    # Session 2: events at 110-112
    sp.emit("user", 1.0, 110.0)
    sp.emit("user", 1.0, 112.0)
    sessions = sp.session_window(5.0, "user")
    assert len(sessions) == 2
    assert sessions[0].count == 3
    assert sessions[1].count == 2


def test_key_filtering():
    sp = StreamProcessorService()
    sp.emit("a", 1.0, 100.0)
    sp.emit("b", 2.0, 100.0)
    sp.emit("a", 3.0, 101.0)
    windows = sp.tumbling_window(10.0, "a")
    assert windows[0].count == 2
    assert windows[0].total == 4.0


def test_late_events():
    sp = StreamProcessorService()
    sp.advance_watermark(100.0)
    sp.emit("m", 1.0, 99.0)  # late!
    sp.emit("m", 2.0, 101.0)  # on time
    assert len(sp.get_late_events()) == 1
    assert sp.stats()["late_events"] == 1


def test_all_keys():
    sp = StreamProcessorService()
    sp.emit("a", 1.0, 100.0)
    sp.emit("b", 2.0, 100.0)
    windows = sp.tumbling_window(10.0)  # no key filter
    assert windows[0].count == 2


def test_empty():
    sp = StreamProcessorService()
    assert sp.tumbling_window(5.0) == []
    assert sp.sliding_window(5.0, 1.0) == []
    assert sp.session_window(5.0) == []
