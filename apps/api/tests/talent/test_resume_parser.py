"""Resume parser tests — section extraction and service logic (N18)."""

from app.talent.services.resume_parser import (
    _SECTION_PATTERNS,
    AUTO_EVIDENCE_THRESHOLD,
    ResumeParserService,
)


class TestSectionExtraction:
    def _svc(self):
        # Section extraction is sync and doesn't need DB
        return ResumeParserService.__new__(ResumeParserService)

    def test_detects_education_section(self):
        text = "Summary\nI am a developer.\n\nEducation\nBS Computer Science, MIT 2020"
        svc = self._svc()
        sections = svc.extract_experience_sections(text)
        assert "education" in sections
        assert "MIT" in sections["education"]

    def test_detects_experience_section(self):
        text = "Work Experience\nSoftware Engineer at Google, 2019-2022"
        svc = self._svc()
        sections = svc.extract_experience_sections(text)
        assert "experience" in sections
        assert "Google" in sections["experience"]

    def test_detects_skills_section(self):
        text = "Technical Skills\nPython, JavaScript, React, Docker"
        svc = self._svc()
        sections = svc.extract_experience_sections(text)
        assert "skills" in sections
        assert "Python" in sections["skills"]

    def test_detects_projects_section(self):
        text = "Personal Projects\nBuilt an AI chatbot using GPT-4"
        svc = self._svc()
        sections = svc.extract_experience_sections(text)
        assert "projects" in sections

    def test_detects_certifications_section(self):
        text = "Certifications\nAWS Solutions Architect Associate"
        svc = self._svc()
        sections = svc.extract_experience_sections(text)
        assert "certifications" in sections

    def test_multiple_sections(self):
        text = (
            "Summary\nExperienced developer\n\n"
            "Education\nBS CS, MIT\n\n"
            "Work Experience\nSenior Eng at Google\n\n"
            "Skills\nPython, ML"
        )
        svc = self._svc()
        sections = svc.extract_experience_sections(text)
        assert "education" in sections
        assert "experience" in sections
        assert "skills" in sections

    def test_no_sections_goes_to_other(self):
        text = "Just some random text without any section headers."
        svc = self._svc()
        sections = svc.extract_experience_sections(text)
        assert "other" in sections

    def test_long_line_not_treated_as_header(self):
        text = "I have extensive education in computer science and machine learning that spans many years of dedicated study and practice in the field"
        svc = self._svc()
        sections = svc.extract_experience_sections(text)
        # Long line shouldn't trigger section detection
        assert "education" not in sections


class TestConstants:
    def test_auto_evidence_threshold(self):
        assert AUTO_EVIDENCE_THRESHOLD == 0.80

    def test_section_patterns_defined(self):
        assert "education" in _SECTION_PATTERNS
        assert "experience" in _SECTION_PATTERNS
        assert "skills" in _SECTION_PATTERNS
        assert "projects" in _SECTION_PATTERNS
        assert "certifications" in _SECTION_PATTERNS
        assert "summary" in _SECTION_PATTERNS
