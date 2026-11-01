import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_search_index import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiSearchIndex, SearchDocument,
)

class TestConsumerApiSearchIndex:
    def test_index_and_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiSearchIndex()
        svc.index("inst-1", SearchDocument(doc_id="d1", doc_type="endpoint", title="List Users", content="GET /api/users returns all users"))
        results = svc.search("inst-1", "users")
        assert len(results) == 1 and results[0].title == "List Users"

    def test_multi_token_scoring(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiSearchIndex()
        svc.index("inst-1", SearchDocument(doc_id="d1", doc_type="endpoint", title="List Users", content="users endpoint"))
        svc.index("inst-1", SearchDocument(doc_id="d2", doc_type="doc", title="Auth Guide", content="authentication guide"))
        results = svc.search("inst-1", "users endpoint")
        assert results[0].doc_id == "d1"  # higher score

    def test_filter_by_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiSearchIndex()
        svc.index("inst-1", SearchDocument(doc_id="d1", doc_type="endpoint", title="API", content="users"))
        svc.index("inst-1", SearchDocument(doc_id="d2", doc_type="doc", title="Doc", content="users"))
        results = svc.search("inst-1", "users", doc_type="doc")
        assert len(results) == 1 and results[0].doc_type == "doc"

    def test_remove(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiSearchIndex()
        svc.index("inst-1", SearchDocument(doc_id="d1", doc_type="endpoint", title="X", content="y"))
        svc.remove("inst-1", "d1")
        assert len(svc.search("inst-1", "y")) == 0

    def test_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiSearchIndex()
        svc.index("inst-1", SearchDocument(doc_id="d1", doc_type="endpoint", title="A", content="x"))
        svc.index("inst-1", SearchDocument(doc_id="d2", doc_type="doc", title="B", content="y"))
        counts = svc.count("inst-1")
        assert counts["endpoint"] == 1 and counts["doc"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiSearchIndex()
        svc.index("inst-1", SearchDocument(doc_id="d1", doc_type="endpoint", title="X", content="y"))
        assert len(svc.search("inst-2", "y")) == 0
