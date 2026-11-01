from app.services.app_api_developer_api_documentation_score import AppAPIDeveloperAPIDocumentationScore

class TestDocScore:
    def test_score(self):
        d = AppAPIDeveloperAPIDocumentationScore()
        s = d.update("inst-1", endpoint_coverage_pct=90, example_coverage_pct=80, error_doc_coverage_pct=70)
        assert s.overall_score == 80.0
        assert s.grade == "B"

    def test_grade_a(self):
        d = AppAPIDeveloperAPIDocumentationScore()
        s = d.update("inst-1", endpoint_coverage_pct=95, example_coverage_pct=92, error_doc_coverage_pct=90)
        assert s.grade == "A"

    def test_isolation(self):
        d = AppAPIDeveloperAPIDocumentationScore()
        d.update("inst-1", endpoint_coverage_pct=50)
        assert d.get("inst-2").overall_score == 0.0
