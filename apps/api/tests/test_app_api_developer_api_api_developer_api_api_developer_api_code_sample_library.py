import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_code_sample_library import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibrary

class TestCodeSampleLibrary:
    def test_add(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibrary()
        s = l.add("inst-1", "s1", "List Users", "python", "/api/users", "requests.get('/api/users')")
        assert s.language == "python"

    def test_invalid_language(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibrary()
        with pytest.raises(ValueError):
            l.add("inst-1", "s1", "X", "brainfuck", "/api", "code")

    def test_view_and_copy(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibrary()
        l.add("inst-1", "s1", "X", "python", "/api", "code")
        l.view("inst-1", "s1")
        l.copy("inst-1", "s1")
        p = l.popular("inst-1")[0]
        assert p.views == 1
        assert p.copies == 1

    def test_by_language(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibrary()
        l.add("inst-1", "s1", "Py", "python", "/api", "code")
        l.add("inst-1", "s2", "JS", "javascript", "/api", "code")
        assert len(l.by_language("inst-1", "python")) == 1

    def test_language_counts(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibrary()
        l.add("inst-1", "s1", "A", "python", "/a", "c")
        l.add("inst-1", "s2", "B", "python", "/b", "c")
        l.add("inst-1", "s3", "C", "go", "/c", "c")
        assert l.language_counts("inst-1") == {"python": 2, "go": 1}

    def test_isolation(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibrary()
        l.add("inst-1", "s1", "X", "python", "/api", "code")
        assert len(l.popular("inst-2")) == 0
