from app.services.app_api_developer_api_api_webhook_event_deduplication import AppAPIDeveloperAPIApiWebhookEventDeduplication

class TestEventDeduplication:
    def test_first_event(self):
        d = AppAPIDeveloperAPIApiWebhookEventDeduplication()
        is_dup, h = d.check("inst-1", "push", '{"ref": "main"}')
        assert is_dup is False
        assert len(h) == 32

    def test_duplicate(self):
        d = AppAPIDeveloperAPIApiWebhookEventDeduplication()
        d.check("inst-1", "push", '{"ref": "main"}')
        is_dup, _ = d.check("inst-1", "push", '{"ref": "main"}')
        assert is_dup is True

    def test_different_payload(self):
        d = AppAPIDeveloperAPIApiWebhookEventDeduplication()
        d.check("inst-1", "push", '{"ref": "main"}')
        is_dup, _ = d.check("inst-1", "push", '{"ref": "dev"}')
        assert is_dup is False

    def test_stats(self):
        d = AppAPIDeveloperAPIApiWebhookEventDeduplication()
        d.check("inst-1", "push", "a")
        d.check("inst-1", "push", "a")
        d.check("inst-1", "push", "a")
        s = d.stats("inst-1")
        assert s["active_hashes"] == 1
        assert s["duplicates_caught"] == 2

    def test_expired(self):
        d = AppAPIDeveloperAPIApiWebhookEventDeduplication(ttl_seconds=0)
        d.check("inst-1", "push", "a")
        import time; time.sleep(0.01)
        is_dup, _ = d.check("inst-1", "push", "a")
        assert is_dup is False

    def test_isolation(self):
        d = AppAPIDeveloperAPIApiWebhookEventDeduplication()
        d.check("inst-1", "push", "a")
        is_dup, _ = d.check("inst-2", "push", "a")
        assert is_dup is False
