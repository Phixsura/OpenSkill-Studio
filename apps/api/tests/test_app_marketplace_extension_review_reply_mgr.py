from app.services.app_marketplace_extension_review_reply_mgr import ReviewReplyMgrService

def test_reply():
    svc = ReviewReplyMgrService()
    r = svc.reply("rev-1", "dev-1", "Thanks for your feedback!")
    assert r.content == "Thanks for your feedback!"

def test_no_duplicate_reply():
    svc = ReviewReplyMgrService()
    svc.reply("rev-1", "dev-1", "Thanks!")
    try:
        svc.reply("rev-1", "dev-1", "Another reply")
        assert False
    except ValueError:
        pass

def test_edit():
    svc = ReviewReplyMgrService()
    svc.reply("rev-1", "dev-1", "Thanks!")
    assert svc.edit("rev-1", "dev-1", "Updated thanks!") is True
    assert svc.get("rev-1").content == "Updated thanks!"
    assert svc.edit("rev-1", "dev-2", "Hack") is False

def test_delete():
    svc = ReviewReplyMgrService()
    svc.reply("rev-1", "dev-1", "Thanks!")
    assert svc.delete("rev-1", "dev-1") is True
    assert svc.get("rev-1") is None
