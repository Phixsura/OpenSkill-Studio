from app.services.app_api_developer_platform_sdk_api_developer_knowledge_base import AppAPIDeveloperPlatformSDKApiDeveloperKnowledgeBase

class TestDeveloperKnowledgeBase:
    def test_add(self):
        kb = AppAPIDeveloperPlatformSDKApiDeveloperKnowledgeBase()
        a = kb.add("inst-1", "a1", "Auth Guide", "How to authenticate", "getting_started", ["auth", "api-key"])
        assert a.category == "getting_started"

    def test_search(self):
        kb = AppAPIDeveloperPlatformSDKApiDeveloperKnowledgeBase()
        kb.add("inst-1", "a1", "Authentication Guide", "How to auth", "getting_started")
        kb.add("inst-1", "a2", "Rate Limits", "How rate limits work", "api_reference")
        results = kb.search("inst-1", "auth")
        assert len(results) == 1
        assert results[0].article_id == "a1"

    def test_popular(self):
        kb = AppAPIDeveloperPlatformSDKApiDeveloperKnowledgeBase()
        kb.add("inst-1", "a1", "A", "c", "faq")
        kb.add("inst-1", "a2", "B", "c", "faq")
        for _ in range(10): kb.view("inst-1", "a2")
        for _ in range(5): kb.view("inst-1", "a1")
        assert kb.popular("inst-1", 1)[0].article_id == "a2"

    def test_category_counts(self):
        kb = AppAPIDeveloperPlatformSDKApiDeveloperKnowledgeBase()
        kb.add("inst-1", "a1", "A", "c", "faq")
        kb.add("inst-1", "a2", "B", "c", "troubleshooting")
        assert kb.category_counts("inst-1") == {"faq": 1, "troubleshooting": 1}

    def test_isolation(self):
        kb = AppAPIDeveloperPlatformSDKApiDeveloperKnowledgeBase()
        kb.add("inst-1", "a1", "A", "c", "faq")
        assert len(kb.popular("inst-2")) == 0
