from app.services.app_marketplace_webhook_transformer import (
    WebhookTransformer, TransformRule,
)


def test_copy_transform():
    wt = WebhookTransformer()
    wt.register_template("simple", [
        TransformRule("name", "user.name", "data.user_name"),
        TransformRule("email", "user.email", "data.contact"),
    ])
    result = wt.transform({"user": {"name": "Alice", "email": "a@b.com"}}, "simple")
    assert result["data"]["user_name"] == "Alice"
    assert result["data"]["contact"] == "a@b.com"


def test_template_transform():
    wt = WebhookTransformer()
    wt.register_template("notify", [
        TransformRule("msg", "{event_type}: {message}", "text", "template"),
    ])
    result = wt.transform({"event_type": "install", "message": "New install!"}, "notify")
    assert result["text"] == "install: New install!"


def test_default_transform():
    wt = WebhookTransformer()
    wt.register_template("with_default", [
        TransformRule("region", "region", "target_region", "default"),
    ])
    result = wt.transform({}, "with_default", defaults={"region": "us-east-1"})
    assert result["target_region"] == "us-east-1"


def test_omit_transform():
    wt = WebhookTransformer()
    wt.register_template("filtered", [
        TransformRule("keep", "name", "name"),
        TransformRule("drop", "secret", "", "omit"),
    ])
    result = wt.transform({"name": "test", "secret": "hidden"}, "filtered")
    assert "name" in result
    assert "secret" not in result


def test_to_slack():
    wt = WebhookTransformer()
    slack = wt.to_slack("extension.published", {"message": "v2.0 released!", "url": "https://example.com"})
    assert "extension.published" in slack["text"]
    assert len(slack["blocks"]) == 2


def test_to_discord():
    wt = WebhookTransformer()
    discord = wt.to_discord("review.created", {"message": "5 stars!", "author": "alice"})
    assert len(discord["embeds"]) == 1
    assert discord["embeds"][0]["description"] == "5 stars!"


def test_passthrough():
    wt = WebhookTransformer()
    result = wt.transform({"key": "value"}, "nonexistent_template")
    assert result == {"key": "value"}
