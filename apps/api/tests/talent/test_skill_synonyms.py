"""Skill synonym resolution tests — pure logic, no DB needed."""

from app.talent.services.skill_synonyms import (
    _REVERSE_SYNONYMS,
    BUILTIN_SYNONYMS,
    FUZZY_THRESHOLD,
)


class TestBuiltinSynonyms:
    def test_has_common_abbreviations(self):
        assert "javascript" in BUILTIN_SYNONYMS
        assert "js" in [a.lower() for a in BUILTIN_SYNONYMS["javascript"]]

    def test_python_aliases(self):
        assert "py" in BUILTIN_SYNONYMS["python"]
        assert "python3" in BUILTIN_SYNONYMS["python"]

    def test_ml_alias(self):
        assert "ml" in BUILTIN_SYNONYMS["machine learning"]

    def test_ai_alias(self):
        assert "ai" in BUILTIN_SYNONYMS["artificial intelligence"]

    def test_k8s_alias(self):
        assert "k8s" in BUILTIN_SYNONYMS["kubernetes"]

    def test_react_aliases(self):
        assert "reactjs" in BUILTIN_SYNONYMS["react"]
        assert "react.js" in BUILTIN_SYNONYMS["react"]

    def test_cloud_providers(self):
        assert "aws" in BUILTIN_SYNONYMS
        assert "gcp" in BUILTIN_SYNONYMS
        assert "azure" in BUILTIN_SYNONYMS


class TestReverseSynonyms:
    def test_js_resolves_to_javascript(self):
        assert _REVERSE_SYNONYMS["js"] == "javascript"

    def test_ml_resolves_to_machine_learning(self):
        assert _REVERSE_SYNONYMS["ml"] == "machine learning"

    def test_k8s_resolves_to_kubernetes(self):
        assert _REVERSE_SYNONYMS["k8s"] == "kubernetes"

    def test_case_insensitive_keys(self):
        # All keys should be lowercase
        for key in _REVERSE_SYNONYMS:
            assert key == key.lower()

    def test_all_aliases_are_in_reverse(self):
        for canonical, aliases in BUILTIN_SYNONYMS.items():
            for alias in aliases:
                assert alias.lower() in _REVERSE_SYNONYMS
                assert _REVERSE_SYNONYMS[alias.lower()] == canonical


class TestFuzzyThreshold:
    def test_threshold_is_reasonable(self):
        assert 0.70 <= FUZZY_THRESHOLD <= 0.95

    def test_threshold_is_float(self):
        assert isinstance(FUZZY_THRESHOLD, float)
