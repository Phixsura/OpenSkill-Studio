import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_mutual_tls import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMutualTls, MtlsCert, CertStatus,
)

class TestMutualTls:
    def test_register_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMutualTls()
        fp = "a" * 64
        svc.register_cert("inst-1", MtlsCert(cert_id="c1", consumer_id="consumer-1", fingerprint=fp, subject_cn="api.client.com"))
        cert = svc.verify("inst-1", fp)
        assert cert is not None and cert.subject_cn == "api.client.com"

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMutualTls()
        svc.register_cert("inst-1", MtlsCert(cert_id="c1", consumer_id="c1", fingerprint="b" * 64, subject_cn="x"))
        svc.revoke("inst-1", "c1")
        assert svc.verify("inst-1", "b" * 64) is None

    def test_duplicate_fingerprint(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMutualTls()
        fp = "c" * 64
        svc.register_cert("inst-1", MtlsCert(cert_id="c1", consumer_id="c1", fingerprint=fp, subject_cn="x"))
        with pytest.raises(ValueError, match="already registered"):
            svc.register_cert("inst-1", MtlsCert(cert_id="c2", consumer_id="c2", fingerprint=fp, subject_cn="y"))

    def test_unknown_fingerprint(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMutualTls()
        assert svc.verify("inst-1", "unknown" * 4) is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiMutualTls()
        svc.register_cert("inst-1", MtlsCert(cert_id="c1", consumer_id="c1", fingerprint="d" * 64, subject_cn="x"))
        assert len(svc.list_certs("inst-2")) == 0
