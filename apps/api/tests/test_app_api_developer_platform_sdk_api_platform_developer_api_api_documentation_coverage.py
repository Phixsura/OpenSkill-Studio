import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_documentation_coverage import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDocumentationCoverage

class TestApiDocumentationCoverage:
    def test_register_and_coverage(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDocumentationCoverage()
        doc = svc.register_endpoint("inst-1", "/users", "GET")
        assert doc.coverage_pct == 0.0

    def test_update_coverage(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDocumentationCoverage()
        svc.register_endpoint("inst-1", "/users", "GET")
        doc = svc.update_coverage("inst-1", "/users", "GET", has_description=True, has_response_schema=True)
        assert doc.coverage_pct == 40.0

    def test_fully_documented(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDocumentationCoverage()
        svc.register_endpoint("inst-1", "/users", "GET")
        svc.update_coverage("inst-1", "/users", "GET", has_description=True, has_request_schema=True, has_response_schema=True, has_examples=True, has_error_codes=True)
        assert svc.list_docs("inst-1")[0].fully_documented is True
        assert len(svc.undocumented("inst-1")) == 0

    def test_overall_coverage(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDocumentationCoverage()
        svc.register_endpoint("inst-1", "/a", "GET")
        svc.register_endpoint("inst-1", "/b", "GET")
        svc.update_coverage("inst-1", "/a", "GET", has_description=True, has_request_schema=True, has_response_schema=True, has_examples=True, has_error_codes=True)
        # /a = 100%, /b = 0% → overall = 50%
        assert svc.overall_coverage("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDocumentationCoverage()
        svc.register_endpoint("inst-1", "/a", "GET")
        assert svc.endpoint_count("inst-2") == 0
