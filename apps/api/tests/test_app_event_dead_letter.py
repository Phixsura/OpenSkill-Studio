from app.services.app_event_dead_letter import add_dead_letter, get_dead_letters, retry_dead_letter, get_dead_letter_count, purge_dead_letters

APP = "dl-test"

def test_add_get():
    add_dead_letter(app_id=APP, event_id="e1", event_type="app.installed", url="https://x.com", error="timeout", attempts=5)
    assert get_dead_letter_count(APP) >= 1

def test_get():
    add_dead_letter(app_id="dl2", event_id="e2", event_type="t", url="u", error="err", attempts=3)
    dls = get_dead_letters("dl2")
    assert len(dls) >= 1

def test_retry():
    add_dead_letter(app_id="dl3", event_id="e3", event_type="t", url="u", error="err", attempts=3)
    dl = retry_dead_letter("dl3", "e3")
    assert dl is not None
    assert get_dead_letter_count("dl3") == 0

def test_retry_missing():
    assert retry_dead_letter("dl4", "nonexist") is None

def test_purge():
    add_dead_letter(app_id="dl5", event_id="e5", event_type="t", url="u", error="err", attempts=1)
    count = purge_dead_letters("dl5")
    assert count >= 1
    assert get_dead_letter_count("dl5") == 0
