from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_sdk_code_sample import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSdkCodeSample

class TestSdkCodeSample:
    def test_generate_curl(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSdkCodeSample()
        sample = svc.generate("inst-1", "/users", "GET", "curl")
        assert "curl" in sample.code and "/users" in sample.code

    def test_generate_python(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSdkCodeSample()
        sample = svc.generate("inst-1", "/orders", "POST", "python")
        assert "requests" in sample.code

    def test_generate_typescript(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSdkCodeSample()
        sample = svc.generate("inst-1", "/api", "GET", "typescript")
        assert "fetch" in sample.code

    def test_languages_available(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSdkCodeSample()
        svc.generate("inst-1", "/api", "GET", "python")
        svc.generate("inst-1", "/api", "GET", "curl")
        langs = svc.languages_available("inst-1", "/api")
        assert "python" in langs and "curl" in langs

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSdkCodeSample()
        svc.generate("inst-1", "/api", "GET", "curl")
        assert svc.total_samples("inst-2") == 0
