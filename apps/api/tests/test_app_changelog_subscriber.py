from app.services.app_changelog_subscriber import subscribe, unsubscribe, is_subscribed, get_subscriber_count

def test_subscribe():
    assert subscribe("cs1", "u1") is True
    assert is_subscribed("cs1", "u1") is True

def test_duplicate():
    subscribe("cs2", "u1")
    assert subscribe("cs2", "u1") is False

def test_unsubscribe():
    subscribe("cs3", "u1")
    assert unsubscribe("cs3", "u1") is True
    assert is_subscribed("cs3", "u1") is False

def test_count():
    subscribe("cs4", "u1")
    subscribe("cs4", "u2")
    assert get_subscriber_count("cs4") == 2
