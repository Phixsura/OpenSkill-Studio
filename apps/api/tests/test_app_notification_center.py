from app.services.app_notification_center import add_notification, get_notifications, get_unread_count, mark_all_read

def test_add_get():
    add_notification("nc1", title="New install", message="App installed", type="success")
    assert len(get_notifications("nc1")) >= 1

def test_unread_count():
    add_notification("nc2", title="T", message="M")
    assert get_unread_count("nc2") >= 1

def test_mark_read():
    add_notification("nc3", title="T", message="M")
    mark_all_read("nc3")
    assert get_unread_count("nc3") == 0

def test_unread_filter():
    add_notification("nc4", title="A", message="M")
    mark_all_read("nc4")
    add_notification("nc4", title="B", message="M")
    unread = get_notifications("nc4", unread_only=True)
    assert len(unread) == 1
