from app.services.app_api_developer_platform_sdk_api_developer_api_documentation_feedback import AppAPIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedback

class TestDocumentationFeedback:
    def test_submit(self):
        f = AppAPIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedback()
        fb = f.submit("inst-1", "f1", "/docs/auth", True, "Great guide!")
        assert fb.helpful is True

    def test_helpfulness_rate(self):
        f = AppAPIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedback()
        f.submit("inst-1", "f1", "/docs/auth", True)
        f.submit("inst-1", "f2", "/docs/auth", True)
        f.submit("inst-1", "f3", "/docs/auth", False)
        assert f.helpfulness_rate("inst-1", "/docs/auth") == 66.7

    def test_worst_pages(self):
        f = AppAPIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedback()
        for i in range(5): f.submit("inst-1", f"f{i}", "/docs/good", True)
        for i in range(5): f.submit("inst-1", f"g{i}", "/docs/bad", False)
        worst = f.worst_pages("inst-1", 1)
        assert worst[0][0] == "/docs/bad"

    def test_recent_comments(self):
        f = AppAPIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedback()
        f.submit("inst-1", "f1", "/docs", True, "Nice!")
        f.submit("inst-1", "f2", "/docs", False)  # no comment
        assert len(f.recent_comments("inst-1")) == 1

    def test_isolation(self):
        f = AppAPIDeveloperPlatformSDKApiDeveloperApiDocumentationFeedback()
        f.submit("inst-1", "f1", "/docs", True)
        assert f.total_feedback("inst-2") == 0
