from app.services.app_api_developer_api_openapi_diff_checker import AppAPIDeveloperAPIOpenAPIDiffChecker

class TestDiffChecker:
    def test_compare(self):
        c = AppAPIDeveloperAPIOpenAPIDiffChecker()
        r = c.compare("inst-1", "v1", "v2", [
            {"diff_id": "d1", "change_type": "breaking", "category": "endpoint_removed", "path": "/api/old", "description": "Removed /api/old"},
            {"diff_id": "d2", "change_type": "non_breaking", "category": "endpoint_added", "path": "/api/new", "description": "Added /api/new"},
        ])
        assert r.breaking_count == 1
        assert r.has_breaking is True

    def test_no_breaking(self):
        c = AppAPIDeveloperAPIOpenAPIDiffChecker()
        r = c.compare("inst-1", "v1", "v2", [
            {"diff_id": "d1", "change_type": "non_breaking", "category": "field_added", "path": "/api/users", "description": "Added field"},
        ])
        assert r.has_breaking is False

    def test_breaking_changes_filter(self):
        c = AppAPIDeveloperAPIOpenAPIDiffChecker()
        c.compare("inst-1", "v1", "v2", [
            {"diff_id": "d1", "change_type": "breaking", "category": "field_removed", "path": "/a", "description": "x"},
            {"diff_id": "d2", "change_type": "non_breaking", "category": "field_added", "path": "/b", "description": "y"},
        ])
        assert len(c.breaking_changes("inst-1", "v1", "v2")) == 1

    def test_isolation(self):
        c = AppAPIDeveloperAPIOpenAPIDiffChecker()
        c.compare("inst-1", "v1", "v2", [])
        assert len(c.list_reports("inst-2")) == 0
