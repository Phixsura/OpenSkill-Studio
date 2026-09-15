"""Tests for gaps #36-50: Passport & Privacy Intelligence."""

from app.talent.services.passport_intelligence import (
    DEFAULT_FIELD_SETS,
    compare_passport_snapshots,
    compute_passport_analytics,
    compute_revision_summary,
    compute_visible_fields,
    generate_embed_code,
    generate_passport_html,
    generate_qr_data,
    generate_verification_badge_svg,
)


# Gap #36: PDF export
class TestPDFExport:
    def test_generates_html(self):
        html = generate_passport_html({"capabilities": [
            {"capability_name": "AI Design", "level": 4, "level_label": "Commercial", "score": 0.84, "evidence_count": 10},
        ]})
        assert "<html>" in html
        assert "AI Design" in html
        assert "L4" in html

    def test_empty_capabilities(self):
        html = generate_passport_html({"capabilities": []})
        assert "<html>" in html


# Gap #37: QR code
class TestQRCode:
    def test_generates_url(self):
        data = generate_qr_data("abc123")
        assert "/verify/passport/abc123" in data["url"]
        assert data["share_token"] == "abc123"

    def test_custom_base_url(self):
        data = generate_qr_data("tok", base_url="https://custom.com")
        assert "custom.com" in data["url"]


# Gap #39: Snapshot comparison
class TestSnapshotComparison:
    def test_added_capability(self):
        a = {"capabilities": []}
        b = {"capabilities": [{"capability_id": "c1", "capability_name": "AI", "level": 3, "score": 0.7}]}
        diff = compare_passport_snapshots(a, b)
        assert len(diff["added"]) == 1
        assert diff["added"][0]["new_level"] == 3

    def test_removed_capability(self):
        a = {"capabilities": [{"capability_id": "c1", "capability_name": "AI", "level": 3, "score": 0.7}]}
        b = {"capabilities": []}
        diff = compare_passport_snapshots(a, b)
        assert len(diff["removed"]) == 1

    def test_changed_level(self):
        a = {"capabilities": [{"capability_id": "c1", "capability_name": "AI", "level": 2, "score": 0.5}]}
        b = {"capabilities": [{"capability_id": "c1", "capability_name": "AI", "level": 4, "score": 0.8}]}
        diff = compare_passport_snapshots(a, b)
        assert len(diff["changed"]) == 1
        assert diff["changed"][0]["score_delta"] > 0

    def test_no_changes(self):
        caps = [{"capability_id": "c1", "capability_name": "AI", "level": 3, "score": 0.7}]
        diff = compare_passport_snapshots({"capabilities": caps}, {"capabilities": caps})
        assert diff["unchanged_count"] == 1
        assert len(diff["added"]) == 0


# Gap #41: Passport analytics
class TestPassportAnalytics:
    def test_empty_views(self):
        result = compute_passport_analytics([])
        assert result["total_views"] == 0

    def test_with_views(self):
        views = [
            {"viewer_type": "employer", "viewer_id": "e1"},
            {"viewer_type": "employer", "viewer_id": "e2"},
            {"viewer_type": "public", "viewer_ip": "1.2.3.4"},
        ]
        result = compute_passport_analytics(views)
        assert result["total_views"] == 3
        assert result["unique_viewers"] == 3
        assert result["views_by_type"]["employer"] == 2


# Gap #44: Granular consent / #50: Data minimization
class TestGranularConsent:
    def test_private_returns_empty(self):
        fields = compute_visible_fields("private", None, None, None)
        assert fields == []

    def test_specific_employer_allowed(self):
        fields = compute_visible_fields("specific_employer", None, "org1", ["org1", "org2"])
        assert len(fields) > 0

    def test_specific_employer_denied(self):
        fields = compute_visible_fields("specific_employer", None, "org3", ["org1"])
        assert fields == []

    def test_custom_visible_fields(self):
        fields = compute_visible_fields("share_link", ["capabilities"], None, None)
        assert fields == ["capabilities"]

    def test_public_subset_minimal(self):
        fields = compute_visible_fields("public_subset", None, None, None)
        assert fields == DEFAULT_FIELD_SETS["minimal"]


# Gap #45: Embedding
class TestEmbedding:
    def test_generates_iframe(self):
        result = generate_embed_code("abcdef12345678")
        assert "<iframe" in result["iframe_code"]
        assert "abcdef12345678" in result["iframe_code"]
        assert result["width"] == 400

    def test_custom_dimensions(self):
        result = generate_embed_code("valid-token-here", width=600, height=400)
        assert result["width"] == 600


# Gap #46: Social proof badge
class TestVerificationBadge:
    def test_generates_svg(self):
        svg = generate_verification_badge_svg(5, 3)
        assert "<svg" in svg
        assert "5 skills" in svg
        assert "L3" in svg

    def test_zero_skills(self):
        svg = generate_verification_badge_svg(0, 0)
        assert "0 skills" in svg


# Gap #47: Revision history
class TestRevisionHistory:
    def test_single_snapshot(self):
        snapshots = [{"id": "s1", "issued_at": "2026-01-01", "payload": {"capabilities": []}}]
        revisions = compute_revision_summary(snapshots)
        assert len(revisions) == 1
        assert "Initial" in revisions[0]["changes"]

    def test_multiple_snapshots(self):
        snapshots = [
            {"id": "s1", "issued_at": "2026-01-01", "payload": {"capabilities": []}},
            {"id": "s2", "issued_at": "2026-02-01", "payload": {"capabilities": [
                {"capability_id": "c1", "capability_name": "AI", "level": 3, "score": 0.7},
            ]}},
        ]
        revisions = compute_revision_summary(snapshots)
        assert len(revisions) == 2
        assert "+1" in revisions[1]["changes"]

    def test_empty(self):
        assert compute_revision_summary([]) == []
