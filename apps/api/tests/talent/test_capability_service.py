"""Capability service tests — slugify + validation logic, no DB needed."""

from app.talent.services.capability import MAX_TRAVERSAL_DEPTH, slugify


class TestSlugify:
    def test_basic(self):
        assert slugify("AI Product Visual Design") == "ai-product-visual-design"

    def test_special_chars(self):
        assert slugify("C++ Programming!") == "c-programming"

    def test_multiple_spaces(self):
        assert slugify("  Hello   World  ") == "hello-world"

    def test_underscores(self):
        assert slugify("machine_learning") == "machine-learning"

    def test_already_slugified(self):
        assert slugify("my-slug") == "my-slug"

    def test_empty(self):
        assert slugify("") == ""

    def test_unicode(self):
        # Non-ASCII stripped, only a-z0-9 kept
        result = slugify("Données AI")
        assert "ai" in result

    def test_numbers(self):
        assert slugify("Python 3.12") == "python-312"

    def test_consecutive_hyphens(self):
        assert slugify("a - - b") == "a-b"


class TestConstants:
    def test_max_traversal_depth(self):
        assert MAX_TRAVERSAL_DEPTH == 20


class TestEdgeTypes:
    def test_edge_types_exist(self):
        from app.talent.models.capability import EDGE_TYPES
        assert "requires" in EDGE_TYPES
        assert "related_to" in EDGE_TYPES
        assert "specializes" in EDGE_TYPES
        assert "subsumes" in EDGE_TYPES
        assert "commonly_paired_with" in EDGE_TYPES
        assert len(EDGE_TYPES) == 5

    def test_mapping_source_types(self):
        from app.talent.models.capability import MAPPING_SOURCE_TYPES
        assert "skill" in MAPPING_SOURCE_TYPES
        assert "skill_pack" in MAPPING_SOURCE_TYPES
        assert "assessment_blueprint" in MAPPING_SOURCE_TYPES
        assert len(MAPPING_SOURCE_TYPES) == 7
