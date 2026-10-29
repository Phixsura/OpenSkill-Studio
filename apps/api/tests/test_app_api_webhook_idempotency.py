from app.services.app_api_webhook_idempotency import AppAPIWebhookIdempotency

class TestIdempotency:
    def test_first_is_not_duplicate(self):
        i = AppAPIWebhookIdempotency()
        key = i.generate_key("push", '{"ref":"main"}', "https://a.com")
        is_dup, _ = i.check_and_record("inst-1", key, "push", "https://a.com")
        assert is_dup is False

    def test_second_is_duplicate(self):
        i = AppAPIWebhookIdempotency()
        key = i.generate_key("push", '{"ref":"main"}', "https://a.com")
        i.check_and_record("inst-1", key, "push", "https://a.com")
        is_dup, _ = i.check_and_record("inst-1", key, "push", "https://a.com")
        assert is_dup is True

    def test_different_payload_different_key(self):
        i = AppAPIWebhookIdempotency()
        k1 = i.generate_key("push", '{"ref":"main"}', "https://a.com")
        k2 = i.generate_key("push", '{"ref":"dev"}', "https://a.com")
        assert k1 != k2

    def test_isolation(self):
        i = AppAPIWebhookIdempotency()
        key = i.generate_key("push", "{}", "https://a.com")
        i.check_and_record("inst-1", key, "push", "https://a.com")
        assert i.count("inst-2") == 0
