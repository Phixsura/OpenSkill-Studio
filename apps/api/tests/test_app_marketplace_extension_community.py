from app.services.app_marketplace_extension_community import ExtensionCommunityService


def test_create_and_reply():
    svc = ExtensionCommunityService()
    t = svc.create_thread("How to deploy?", "Need help", "alice", ["deploy"])
    svc.reply(t.thread_id)
    svc.reply(t.thread_id)
    assert t.reply_count == 2


def test_upvote():
    svc = ExtensionCommunityService()
    t = svc.create_thread("Best practices?", "Tips please", "bob")
    assert svc.upvote(t.thread_id) == 1
    assert svc.upvote(t.thread_id) == 2


def test_trending():
    svc = ExtensionCommunityService()
    t1 = svc.create_thread("Hot topic", "Trending", "alice")
    t2 = svc.create_thread("Cold topic", "Not popular", "bob")
    for _ in range(10):
        svc.upvote(t1.thread_id)
    trending = svc.get_trending(1)
    assert trending[0].title == "Hot topic"


def test_unanswered():
    svc = ExtensionCommunityService()
    t1 = svc.create_thread("Q1", "?", "a")
    t2 = svc.create_thread("Q2", "?", "b")
    svc.mark_answered(t1.thread_id)
    unanswered = svc.get_unanswered()
    assert len(unanswered) == 1
    assert unanswered[0].title == "Q2"


def test_search():
    svc = ExtensionCommunityService()
    svc.create_thread("Webhook help", "How to set up webhooks", "alice", ["webhook"])
    svc.create_thread("Auth question", "OAuth flow", "bob", ["auth"])
    results = svc.search("webhook")
    assert len(results) == 1


def test_stats():
    svc = ExtensionCommunityService()
    t = svc.create_thread("Q", "?", "a")
    svc.reply(t.thread_id)
    svc.upvote(t.thread_id)
    stats = svc.get_stats()
    assert stats["total_threads"] == 1
    assert stats["total_replies"] == 1
    assert stats["total_upvotes"] == 1
