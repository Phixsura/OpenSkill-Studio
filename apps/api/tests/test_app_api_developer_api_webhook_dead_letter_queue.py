from app.services.app_api_developer_api_webhook_dead_letter_queue import AppAPIDeveloperAPIWebhookDeadLetterQueue

class TestDeadLetterQueue:
    def test_enqueue(self):
        q = AppAPIDeveloperAPIWebhookDeadLetterQueue()
        dl = q.enqueue("inst-1", "dl1", "push", "https://a.com", "{}", "timeout", 3)
        assert dl.retry_count == 3

    def test_peek(self):
        q = AppAPIDeveloperAPIWebhookDeadLetterQueue()
        q.enqueue("inst-1", "dl1", "push", "https://a.com", "{}", "timeout", 3)
        q.enqueue("inst-1", "dl2", "issue", "https://b.com", "{}", "500", 5)
        items = q.peek("inst-1")
        assert items[0].letter_id == "dl2"

    def test_requeue(self):
        q = AppAPIDeveloperAPIWebhookDeadLetterQueue()
        q.enqueue("inst-1", "dl1", "push", "https://a.com", "{}", "timeout", 3)
        dl = q.requeue("inst-1", "dl1")
        assert dl.requeued is True

    def test_purge_by_destination(self):
        q = AppAPIDeveloperAPIWebhookDeadLetterQueue()
        q.enqueue("inst-1", "dl1", "push", "https://a.com", "{}", "timeout", 3)
        q.enqueue("inst-1", "dl2", "push", "https://b.com", "{}", "500", 5)
        assert q.purge("inst-1", "https://a.com") == 1
        assert q.count("inst-1") == 1

    def test_isolation(self):
        q = AppAPIDeveloperAPIWebhookDeadLetterQueue()
        q.enqueue("inst-1", "dl1", "push", "https://a.com", "{}", "timeout", 3)
        assert q.count("inst-2") == 0
