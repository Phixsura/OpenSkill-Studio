"""Parametrized tests verifying event category completeness."""

import pytest
from app.services.event_dispatch import CANONICAL_EVENTS

EXPECTED_CATEGORIES = {
    "org": ["org.created", "org.updated", "org.member_added", "org.member_removed"],
    "cohort": ["cohort.created", "cohort.updated", "cohort.member_added", "cohort.member_removed"],
    "project": ["project.created", "project.published", "project.archived"],
    "submission": ["submission.created", "submission.completed", "submission.graded"],
    "pack": ["pack.published", "pack.installed", "pack.updated", "pack.uninstalled", "pack.forked"],
    "workflow": ["workflow.run_started", "workflow.run_completed", "workflow.run_failed"],
    "talent": ["talent.capability_verified", "talent.credential_issued", "talent.credential_revoked"],
    "marketplace": ["marketplace.listing_published", "marketplace.purchase_completed"],
    "evaluation": ["evaluation.completed", "evaluation.failed"],
    "app": ["app.installed", "app.uninstalled", "app.updated"],
}

@pytest.mark.parametrize("category,events", EXPECTED_CATEGORIES.items(), ids=lambda x: x if isinstance(x, str) else "events")
def test_category_events_exist(category, events):
    for event in events:
        assert event in CANONICAL_EVENTS, f"Missing event: {event}"

@pytest.mark.parametrize("category", EXPECTED_CATEGORIES.keys())
def test_category_has_minimum_events(category):
    cat_events = [e for e in CANONICAL_EVENTS if e.startswith(f"{category}.")]
    assert len(cat_events) >= 2, f"Category {category} has too few events"
