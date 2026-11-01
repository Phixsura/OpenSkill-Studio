import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_oauth_client import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerOauthClient, OAuthClient,
)

class TestConsumerOauthClient:
    def test_register_and_auth(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerOauthClient()
        secret, client = svc.register("inst-1", OAuthClient(client_id="app1", consumer_id="c1", client_name="My App", redirect_uris=["https://example.com/cb"]))
        assert svc.authenticate("inst-1", "app1", secret)

    def test_bad_secret(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerOauthClient()
        svc.register("inst-1", OAuthClient(client_id="app1", consumer_id="c1", client_name="My App", redirect_uris=["https://example.com/cb"]))
        assert not svc.authenticate("inst-1", "app1", "wrong_secret")

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerOauthClient()
        secret, _ = svc.register("inst-1", OAuthClient(client_id="app1", consumer_id="c1", client_name="My App", redirect_uris=["https://example.com/cb"]))
        svc.revoke("inst-1", "app1")
        assert not svc.authenticate("inst-1", "app1", secret)

    def test_http_redirect_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerOauthClient()
        with pytest.raises(ValueError, match="HTTPS"):
            svc.register("inst-1", OAuthClient(client_id="app1", consumer_id="c1", client_name="App", redirect_uris=["http://evil.com/cb"]))

    def test_localhost_allowed(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerOauthClient()
        _, client = svc.register("inst-1", OAuthClient(client_id="app1", consumer_id="c1", client_name="Dev", redirect_uris=["http://localhost:3000/cb"]))
        assert client.active

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerOauthClient()
        secret, _ = svc.register("inst-1", OAuthClient(client_id="app1", consumer_id="c1", client_name="App", redirect_uris=["https://x.com/cb"]))
        assert not svc.authenticate("inst-2", "app1", secret)
