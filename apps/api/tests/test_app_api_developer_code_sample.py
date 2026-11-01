import pytest
from app.services.app_api_developer_code_sample import AppAPIDeveloperCodeSample

class TestCodeSample:
    def test_add(self):
        c = AppAPIDeveloperCodeSample()
        s = c.add("inst-1", "s1", "GET /api/users", "python", "import requests\nr = requests.get('/api/users')", "List Users")
        assert s.language == "python"

    def test_empty_code(self):
        c = AppAPIDeveloperCodeSample()
        with pytest.raises(ValueError):
            c.add("inst-1", "s1", "/api", "python", "  ")

    def test_by_language(self):
        c = AppAPIDeveloperCodeSample()
        c.add("inst-1", "s1", "/api", "python", "code")
        c.add("inst-1", "s2", "/api", "javascript", "code")
        assert len(c.by_language("inst-1", "python")) == 1

    def test_copy_count(self):
        c = AppAPIDeveloperCodeSample()
        c.add("inst-1", "s1", "/api", "go", "code")
        c.record_copy("inst-1", "s1")
        assert c.list_samples("inst-1")[0].copy_count == 1

    def test_isolation(self):
        c = AppAPIDeveloperCodeSample()
        c.add("inst-1", "s1", "/api", "python", "code")
        assert c.list_samples("inst-2") == []
