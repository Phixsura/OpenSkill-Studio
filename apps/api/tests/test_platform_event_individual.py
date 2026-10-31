"""Individual canonical event presence tests."""

from app.services.event_dispatch import CANONICAL_EVENTS

def test_org_created(): assert "org.created" in CANONICAL_EVENTS
def test_org_updated(): assert "org.updated" in CANONICAL_EVENTS
def test_org_member_added(): assert "org.member_added" in CANONICAL_EVENTS
def test_org_member_removed(): assert "org.member_removed" in CANONICAL_EVENTS
def test_cohort_created(): assert "cohort.created" in CANONICAL_EVENTS
def test_cohort_updated(): assert "cohort.updated" in CANONICAL_EVENTS
def test_cohort_member_added(): assert "cohort.member_added" in CANONICAL_EVENTS
def test_cohort_member_removed(): assert "cohort.member_removed" in CANONICAL_EVENTS
def test_project_created(): assert "project.created" in CANONICAL_EVENTS
def test_project_published(): assert "project.published" in CANONICAL_EVENTS
def test_project_archived(): assert "project.archived" in CANONICAL_EVENTS
def test_submission_created(): assert "submission.created" in CANONICAL_EVENTS
def test_submission_completed(): assert "submission.completed" in CANONICAL_EVENTS
def test_submission_graded(): assert "submission.graded" in CANONICAL_EVENTS
def test_pack_published(): assert "pack.published" in CANONICAL_EVENTS
def test_pack_installed(): assert "pack.installed" in CANONICAL_EVENTS
def test_pack_updated(): assert "pack.updated" in CANONICAL_EVENTS
def test_pack_uninstalled(): assert "pack.uninstalled" in CANONICAL_EVENTS
def test_pack_forked(): assert "pack.forked" in CANONICAL_EVENTS
def test_workflow_run_started(): assert "workflow.run_started" in CANONICAL_EVENTS
def test_workflow_run_completed(): assert "workflow.run_completed" in CANONICAL_EVENTS
def test_workflow_run_failed(): assert "workflow.run_failed" in CANONICAL_EVENTS
def test_talent_capability_verified(): assert "talent.capability_verified" in CANONICAL_EVENTS
def test_talent_credential_issued(): assert "talent.credential_issued" in CANONICAL_EVENTS
def test_talent_credential_revoked(): assert "talent.credential_revoked" in CANONICAL_EVENTS
def test_marketplace_listing_published(): assert "marketplace.listing_published" in CANONICAL_EVENTS
def test_marketplace_purchase_completed(): assert "marketplace.purchase_completed" in CANONICAL_EVENTS
def test_evaluation_completed(): assert "evaluation.completed" in CANONICAL_EVENTS
def test_evaluation_failed(): assert "evaluation.failed" in CANONICAL_EVENTS
def test_app_installed(): assert "app.installed" in CANONICAL_EVENTS
def test_app_uninstalled(): assert "app.uninstalled" in CANONICAL_EVENTS
def test_app_updated(): assert "app.updated" in CANONICAL_EVENTS
