from app.services.app_marketplace_extension_webhook_secret_rot import WebhookSecretRotService

def test_create_and_sign():
    svc = WebhookSecretRotService()
    svc.create("ext-1")
    sig = svc.sign("ext-1", "test payload")
    assert sig is not None
    assert svc.verify("ext-1", "test payload", sig) is True

def test_rotate_keeps_old_in_grace():
    svc = WebhookSecretRotService()
    old = svc.create("ext-1")
    old_sig = svc.sign("ext-1", "data")
    svc.rotate("ext-1")
    # Old signature still valid during grace
    assert svc.verify("ext-1", "data", old_sig) is True
    # New secret also works
    new_sig = svc.sign("ext-1", "data")
    assert svc.verify("ext-1", "data", new_sig) is True

def test_invalid_signature():
    svc = WebhookSecretRotService()
    svc.create("ext-1")
    assert svc.verify("ext-1", "data", "invalid") is False
