"""Tests for taxonomy import service."""

from app.talent.services.taxonomy_import import (
    SUPPORTED_TAXONOMY_FORMATS,
    TAXONOMY_API_VERSION,
    TAXONOMY_VERSION_INFO,
    compute_changelog,
    get_industry_taxonomy,
    list_available_industries,
    parse_custom_json_row,
    parse_esco_csv_row,
    parse_onet_csv_row,
    validate_import_batch,
)


class TestESCOParser:
    def test_valid(self):
        result = parse_esco_csv_row({"conceptUri": "http://esco/1", "preferredLabel": "Python"})
        assert result is not None
        assert result["canonical_name"] == "Python"

    def test_with_alt_labels(self):
        result = parse_esco_csv_row({"conceptUri": "u", "preferredLabel": "ML", "altLabels": "Machine Learning\nAI"})
        assert len(result["aliases"]) == 2

    def test_empty(self):
        assert parse_esco_csv_row({}) is None

    def test_missing_uri(self):
        assert parse_esco_csv_row({"preferredLabel": "X"}) is None


class TestONETParser:
    def test_valid(self):
        result = parse_onet_csv_row({"O*NET-SOC Code": "15-1252", "Title": "Dev"})
        assert result["external_ids"]["onet_code"] == "15-1252"

    def test_element_id(self):
        result = parse_onet_csv_row({"Element ID": "2.A.1", "Element Name": "Skill"})
        assert result is not None

    def test_empty(self):
        assert parse_onet_csv_row({}) is None


class TestCustomParser:
    def test_valid(self):
        result = parse_custom_json_row({"name": "AI Design", "category": "design"})
        assert result["canonical_name"] == "AI Design"

    def test_with_translations(self):
        result = parse_custom_json_row({"name": "AI", "translations": {"zh": {"name": "人工智能"}}})
        assert result["translations"]["zh"]["name"] == "人工智能"

    def test_empty(self):
        assert parse_custom_json_row({}) is None


class TestValidateImportBatch:
    def test_valid_batch(self):
        rows = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        result = validate_import_batch(rows, "custom_json")
        assert result.created == 3
        assert len(result.errors) == 0

    def test_mixed_batch(self):
        rows = [{"name": "Good"}, {}, {"name": "Also good"}]
        result = validate_import_batch(rows, "custom_json")
        assert result.created == 2
        assert len(result.errors) == 1

    def test_invalid_format(self):
        result = validate_import_batch([], "invalid_format")
        assert len(result.errors) == 1

    def test_empty_batch(self):
        result = validate_import_batch([], "custom_json")
        assert result.total_rows == 0


class TestChangelog:
    def test_detects_changes(self):
        before = {"id": "1", "canonical_name": "Old", "category": "a"}
        after = {"id": "1", "canonical_name": "New", "category": "b"}
        changes = compute_changelog(before, after)
        assert len(changes) == 2

    def test_no_changes(self):
        data = {"id": "1", "canonical_name": "Same", "category": "a"}
        assert len(compute_changelog(data, data)) == 0


class TestIndustryTaxonomies:
    def test_list(self):
        industries = list_available_industries()
        assert len(industries) >= 3

    def test_get_ai(self):
        tax = get_industry_taxonomy("ai_visual_production")
        assert len(tax) >= 5

    def test_get_unknown(self):
        assert get_industry_taxonomy("unknown") == []


class TestConstants:
    def test_formats(self):
        assert len(SUPPORTED_TAXONOMY_FORMATS) == 3

    def test_version(self):
        assert TAXONOMY_API_VERSION == "1.0.0"

    def test_version_info(self):
        assert "api_version" in TAXONOMY_VERSION_INFO
        assert "supported_formats" in TAXONOMY_VERSION_INFO
