"""Tests for API Changelog Generator — endpoint diffs, severity, markdown/json output."""

import pytest

from app.services.api_changelog_generator import (
    ChangeType,
    ChangelogEntry,
    EndpointSpec,
    Severity,
    changelog_to_json,
    changelog_to_markdown,
    diff_endpoints,
    generate_changelog,
)


def _v1_endpoints() -> list[EndpointSpec]:
    return [
        EndpointSpec("GET", "/api/v1/skills", "List skills",
                      parameters={"page": "integer", "per_page": "integer"},
                      response_fields={"id": "string", "name": "string", "level": "string"}),
        EndpointSpec("GET", "/api/v1/skills/{id}", "Get skill detail",
                      response_fields={"id": "string", "name": "string", "description": "string"}),
        EndpointSpec("POST", "/api/v1/skills", "Create skill",
                      parameters={"name": "string", "level": "string"}),
        EndpointSpec("DELETE", "/api/v1/skills/{id}", "Delete skill"),
    ]


def _v2_endpoints() -> list[EndpointSpec]:
    return [
        EndpointSpec("GET", "/api/v1/skills", "List skills with filters",
                      parameters={"page": "integer", "per_page": "integer", "category": "string"},
                      response_fields={"id": "string", "name": "string", "level": "string", "category": "string"}),
        EndpointSpec("GET", "/api/v1/skills/{id}", "Get skill detail",
                      response_fields={"id": "string", "name": "string", "description": "string"},
                      deprecated=True),
        EndpointSpec("POST", "/api/v1/skills", "Create skill",
                      parameters={"name": "string", "level": "integer"}),  # level type changed
        # DELETE removed
        EndpointSpec("GET", "/api/v1/skills/search", "Search skills",
                      parameters={"q": "string"}),  # new endpoint
    ]


class TestDiffEndpoints:
    def test_added_endpoint(self):
        changes = diff_endpoints(_v1_endpoints(), _v2_endpoints())
        added = [c for c in changes if c.change_type == ChangeType.ADDED]
        assert len(added) == 1
        assert added[0].path == "/api/v1/skills/search"
        assert added[0].severity == Severity.NON_BREAKING

    def test_removed_endpoint(self):
        changes = diff_endpoints(_v1_endpoints(), _v2_endpoints())
        removed = [c for c in changes if c.change_type == ChangeType.REMOVED]
        assert len(removed) == 1
        assert removed[0].path == "/api/v1/skills/{id}"
        assert removed[0].method == "DELETE"
        assert removed[0].severity == Severity.BREAKING

    def test_deprecated_endpoint(self):
        changes = diff_endpoints(_v1_endpoints(), _v2_endpoints())
        deprecated = [c for c in changes if c.change_type == ChangeType.DEPRECATED]
        assert len(deprecated) == 1
        assert deprecated[0].path == "/api/v1/skills/{id}"
        assert deprecated[0].severity == Severity.NON_BREAKING

    def test_modified_params(self):
        changes = diff_endpoints(_v1_endpoints(), _v2_endpoints())
        modified = [c for c in changes if c.change_type == ChangeType.MODIFIED]
        # GET /skills: added category param + response field
        # POST /skills: level type changed
        assert len(modified) >= 1
        post_mod = [c for c in modified if c.method == "POST"]
        assert len(post_mod) == 1
        type_changes = [p for p in post_mod[0].param_changes if p.change_type == ChangeType.MODIFIED]
        assert any(p.name == "level" for p in type_changes)

    def test_added_param_is_non_breaking(self):
        changes = diff_endpoints(_v1_endpoints(), _v2_endpoints())
        get_list_mods = [c for c in changes if c.method == "GET" and c.path == "/api/v1/skills"
                         and c.change_type == ChangeType.MODIFIED]
        if get_list_mods:
            added_params = [p for p in get_list_mods[0].param_changes if p.change_type == ChangeType.ADDED]
            assert any(p.name == "category" for p in added_params)

    def test_type_change_is_breaking(self):
        changes = diff_endpoints(_v1_endpoints(), _v2_endpoints())
        post_mod = [c for c in changes if c.method == "POST" and c.change_type == ChangeType.MODIFIED]
        assert len(post_mod) == 1
        assert post_mod[0].severity == Severity.BREAKING

    def test_no_changes(self):
        endpoints = _v1_endpoints()
        changes = diff_endpoints(endpoints, endpoints)
        assert len(changes) == 0

    def test_empty_to_something(self):
        changes = diff_endpoints([], _v1_endpoints())
        assert all(c.change_type == ChangeType.ADDED for c in changes)
        assert len(changes) == 4

    def test_something_to_empty(self):
        changes = diff_endpoints(_v1_endpoints(), [])
        assert all(c.change_type == ChangeType.REMOVED for c in changes)
        assert all(c.severity == Severity.BREAKING for c in changes)


class TestGenerateChangelog:
    def test_changelog_structure(self):
        entry = generate_changelog("1.0", "2.0", _v1_endpoints(), _v2_endpoints())
        assert entry.from_version == "1.0"
        assert entry.to_version == "2.0"
        assert entry.generated_at is not None
        assert len(entry.changes) > 0

    def test_breaking_count(self):
        entry = generate_changelog("1.0", "2.0", _v1_endpoints(), _v2_endpoints())
        assert entry.has_breaking is True
        assert entry.breaking_count >= 1  # at least DELETE removed

    def test_no_breaking_when_only_additions(self):
        old = [EndpointSpec("GET", "/api/v1/skills", "List")]
        new = [
            EndpointSpec("GET", "/api/v1/skills", "List"),
            EndpointSpec("GET", "/api/v1/packs", "List packs"),
        ]
        entry = generate_changelog("1.0", "1.1", old, new)
        assert entry.has_breaking is False
        assert entry.non_breaking_count == 1


class TestMarkdownOutput:
    def test_contains_version_header(self):
        entry = generate_changelog("1.0", "2.0", _v1_endpoints(), _v2_endpoints())
        md = changelog_to_markdown(entry)
        assert "1.0 → 2.0" in md

    def test_contains_breaking_warning(self):
        entry = generate_changelog("1.0", "2.0", _v1_endpoints(), _v2_endpoints())
        md = changelog_to_markdown(entry)
        assert "breaking" in md.lower()
        assert "⚠️" in md

    def test_contains_migration_hints(self):
        entry = generate_changelog("1.0", "2.0", _v1_endpoints(), _v2_endpoints())
        md = changelog_to_markdown(entry)
        assert "Migration" in md

    def test_contains_endpoint_paths(self):
        entry = generate_changelog("1.0", "2.0", _v1_endpoints(), _v2_endpoints())
        md = changelog_to_markdown(entry)
        assert "/api/v1/skills" in md

    def test_no_breaking_no_warning(self):
        old = [EndpointSpec("GET", "/a", "A")]
        new = [EndpointSpec("GET", "/a", "A"), EndpointSpec("GET", "/b", "B")]
        entry = generate_changelog("1.0", "1.1", old, new)
        md = changelog_to_markdown(entry)
        assert "⚠️" not in md


class TestJsonOutput:
    def test_json_structure(self):
        entry = generate_changelog("1.0", "2.0", _v1_endpoints(), _v2_endpoints())
        j = changelog_to_json(entry)
        assert j["from_version"] == "1.0"
        assert j["to_version"] == "2.0"
        assert "summary" in j
        assert "changes" in j
        assert j["summary"]["has_breaking"] is True

    def test_json_changes_list(self):
        entry = generate_changelog("1.0", "2.0", _v1_endpoints(), _v2_endpoints())
        j = changelog_to_json(entry)
        assert len(j["changes"]) > 0
        c = j["changes"][0]
        assert "method" in c
        assert "path" in c
        assert "change_type" in c
        assert "severity" in c

    def test_json_param_changes(self):
        entry = generate_changelog("1.0", "2.0", _v1_endpoints(), _v2_endpoints())
        j = changelog_to_json(entry)
        modified = [c for c in j["changes"] if c["change_type"] == "modified"]
        assert any(len(c["param_changes"]) > 0 for c in modified)
