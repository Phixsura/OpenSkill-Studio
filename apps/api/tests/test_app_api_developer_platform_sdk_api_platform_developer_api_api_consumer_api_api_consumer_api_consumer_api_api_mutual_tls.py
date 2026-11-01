import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_mutual_tls import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiMutualTls, MTLSConfig, ClientCertificate,
)

class TestConsumerApiMutualTls:
    def _now(self):
        return datetime(2026, 6, 1)

    def _fp(self):
        return "a" * 64

    def test_register_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiMutualTls()
        svc.register_cert("inst-1", ClientCertificate(cert_id="c1", consumer_id="con1", subject_cn="api.example.com", fingerprint_sha256=self._fp(), not_before=self._now(), not_after=self._now() + timedelta(days=365)))
        result = svc.verify("inst-1", self._fp(), self._now())
        assert result.valid and result.consumer_id == "con1"

    def test_revoked(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiMutualTls()
        svc.register_cert("inst-1", ClientCertificate(cert_id="c1", consumer_id="con1", subject_cn="x", fingerprint_sha256=self._fp()))
        svc.revoke_cert("inst-1", self._fp())
        result = svc.verify("inst-1", self._fp(), self._now())
        assert not result.valid and result.reason == "cert_revoked"

    def test_expired(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiMutualTls()
        svc.register_cert("inst-1", ClientCertificate(cert_id="c1", consumer_id="con1", subject_cn="x", fingerprint_sha256=self._fp(), not_after=self._now()))
        result = svc.verify("inst-1", self._fp(), self._now() + timedelta(days=1))
        assert not result.valid and result.reason == "cert_expired"

    def test_issuer_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiMutualTls()
        svc.configure("inst-1", MTLSConfig(consumer_id="con1", allowed_issuers=["TrustedCA"]))
        svc.register_cert("inst-1", ClientCertificate(cert_id="c1", consumer_id="con1", subject_cn="x", fingerprint_sha256=self._fp(), issuer="UntrustedCA"))
        result = svc.verify("inst-1", self._fp(), self._now())
        assert not result.valid and result.reason == "issuer_not_allowed"

    def test_not_found(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiMutualTls()
        result = svc.verify("inst-1", "b" * 64, self._now())
        assert not result.valid and result.reason == "cert_not_found"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiMutualTls()
        svc.register_cert("inst-1", ClientCertificate(cert_id="c1", consumer_id="con1", subject_cn="x", fingerprint_sha256=self._fp()))
        assert not svc.verify("inst-2", self._fp(), self._now()).valid
