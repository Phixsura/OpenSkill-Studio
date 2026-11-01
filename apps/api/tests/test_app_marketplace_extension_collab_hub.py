from app.services.app_marketplace_extension_collab_hub import ExtCollabHubService

def test_create_and_reply():
    svc = ExtCollabHubService()
    t = svc.create_thread("ext-1", "API Design", "dev-1", "How should we design the API?")
    svc.reply(t.thread_id, "dev-2", "I suggest REST")
    assert len(t.messages) == 2

def test_resolve():
    svc = ExtCollabHubService()
    t = svc.create_thread("ext-1", "Bug", "dev-1", "Found a bug")
    svc.resolve(t.thread_id)
    assert t.status == "resolved"

def test_locked():
    svc = ExtCollabHubService()
    t = svc.create_thread("ext-1", "Old", "dev-1", "Discussion")
    t.status = "locked"
    assert svc.reply(t.thread_id, "dev-2", "Too late") is False

def test_search():
    svc = ExtCollabHubService()
    svc.create_thread("ext-1", "API Design", "dev-1", "REST vs GraphQL")
    svc.create_thread("ext-1", "UI Bug", "dev-1", "Button broken")
    results = svc.search("graphql")
    assert len(results) == 1
