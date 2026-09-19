"""Tests for gaps #106-130: Employer Intelligence."""

from app.talent.services.employer_intelligence import (
    APPROVAL_STATUSES,
    CUSTOMIZABLE_STAGES,
    DEFAULT_PIPELINE_STAGES,
    INTERVIEW_KIT_SECTIONS,
    POOL_RULE_TYPES,
    build_department_tree,
    build_relationship_timeline,
    compare_offers,
    compute_adverse_impact,
    compute_brand_health_trend,
    compute_offer_deadline_alerts,
    evaluate_pool_rule,
    evaluate_pool_rules,
    generate_interview_kit,
    generate_offer_html,
    validate_custom_pipeline,
    validate_requisition,
)


class TestOfferHTML:
    def test_generates(self):
        html = generate_offer_html({"role_title": "AI Designer", "compensation_text": "$60k"})
        assert "<html>" in html
        assert "AI Designer" in html

    def test_with_conditions(self):
        html = generate_offer_html(
            {"role_title": "Dev", "conditions": ["Background check", "Drug test"]}
        )
        assert "Background check" in html


class TestOfferComparison:
    def test_compare(self):
        offers = [
            {
                "role_title": "A",
                "compensation_text": "$50k",
                "start_date": "2026-03-01",
                "conditions": ["a"],
            },
            {
                "role_title": "B",
                "compensation_text": "$60k-$70k",
                "start_date": "2026-02-01",
                "conditions": [],
            },
        ]
        result = compare_offers(offers)
        assert result.fewest_conditions == 0
        assert len(result.offers) == 2

    def test_empty(self):
        result = compare_offers([])
        assert result.fewest_conditions == 0


class TestOfferDeadlineAlerts:
    def test_no_expiring(self):
        alerts = compute_offer_deadline_alerts([{"id": "o1"}])
        assert alerts == []


class TestDepartmentTree:
    def test_flat(self):
        depts = [{"id": "d1", "name": "Engineering"}, {"id": "d2", "name": "Design"}]
        tree = build_department_tree(depts)
        assert len(tree) == 2

    def test_nested(self):
        depts = [
            {"id": "d1", "name": "Engineering", "parent_department_id": None},
            {"id": "d2", "name": "Frontend", "parent_department_id": "d1"},
        ]
        tree = build_department_tree(depts)
        assert len(tree) == 1
        assert len(tree[0]["children"]) == 1


class TestCustomPipeline:
    def test_valid(self):
        stages = ["submitted", "screening", "interview", "offer", "hired"]
        assert validate_custom_pipeline(stages) == []

    def test_missing_submitted(self):
        errors = validate_custom_pipeline(["screening", "interview", "hired"])
        assert any("submitted" in e for e in errors)

    def test_too_short(self):
        errors = validate_custom_pipeline(["submitted", "hired"])
        assert any("3" in e for e in errors)

    def test_duplicates(self):
        errors = validate_custom_pipeline(["submitted", "screening", "screening", "hired"])
        assert any("duplicate" in e.lower() for e in errors)


class TestPoolRules:
    def test_evaluate_pass(self):
        assert (
            evaluate_pool_rule(
                {"rule_type": "min_capability_level", "field": "level", "value": 3},
                {"level": 4},
            )
            is True
        )

    def test_evaluate_fail(self):
        assert (
            evaluate_pool_rule(
                {"rule_type": "min_capability_level", "field": "level", "value": 5},
                {"level": 2},
            )
            is False
        )

    def test_evaluate_all(self):
        rules = [{"rule_type": "min_capability_level", "field": "level", "value": 2}]
        result = evaluate_pool_rules(rules, {"level": 3})
        assert result["eligible"] is True

    def test_rule_types(self):
        assert len(POOL_RULE_TYPES) >= 5


class TestInterviewKit:
    def test_generates(self):
        opp = {"title": "AI Designer", "required_capabilities": [{"capability_id": "c1"}]}
        kit = generate_interview_kit(opp, "technical")
        assert kit["stage_type"] == "technical"
        assert len(kit["suggested_questions"]) > 0
        assert len(INTERVIEW_KIT_SECTIONS) >= 5


class TestAdverseImpact:
    def test_no_impact(self):
        result = compute_adverse_impact(80, 100, 75, 100)
        assert result["adverse_impact"] is False

    def test_has_impact(self):
        result = compute_adverse_impact(50, 100, 10, 100)
        assert result["adverse_impact"] is True
        assert result["ratio"] < 0.8

    def test_zero_selections(self):
        result = compute_adverse_impact(0, 100, 0, 100)
        assert result["adverse_impact"] is False


class TestRelationshipTimeline:
    def test_builds(self):
        events = [
            {"type": "application", "timestamp": "2026-02-01", "summary": "Applied"},
            {"type": "message", "timestamp": "2026-01-15", "summary": "First contact"},
        ]
        timeline = build_relationship_timeline(events)
        assert len(timeline) == 2
        assert timeline[0]["timestamp"] < timeline[1]["timestamp"]


class TestRequisitionApproval:
    def test_valid(self):
        req = {
            "title": "Senior Dev",
            "department": "Engineering",
            "justification": "Team growth needed for Q3 deliverables",
            "headcount": 2,
        }
        assert validate_requisition(req) == []

    def test_missing_title(self):
        errors = validate_requisition(
            {"department": "Eng", "justification": "Need more people for projects", "headcount": 1}
        )
        assert any("title" in e.lower() for e in errors)

    def test_statuses(self):
        assert "pending_approval" in APPROVAL_STATUSES


class TestBrandHealth:
    def test_improving(self):
        snapshots = [{"reputation_score": 50}, {"reputation_score": 60}]
        result = compute_brand_health_trend(snapshots)
        assert result["trend"] == "improving"

    def test_declining(self):
        snapshots = [{"reputation_score": 70}, {"reputation_score": 55}]
        result = compute_brand_health_trend(snapshots)
        assert result["trend"] == "declining"

    def test_insufficient(self):
        result = compute_brand_health_trend([])
        assert result["trend"] == "insufficient_data"


class TestConstants:
    def test_default_stages(self):
        assert "submitted" in DEFAULT_PIPELINE_STAGES
        assert len(DEFAULT_PIPELINE_STAGES) >= 10

    def test_customizable_stages(self):
        assert "phone_screen" in CUSTOMIZABLE_STAGES
