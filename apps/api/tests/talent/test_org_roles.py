"""OrgRole extension tests — employer roles (ADR-015 §16)."""

import pytest

from app.models.organization import OrgRole, ROLE_HIERARCHY


class TestEmployerRoles:
    """§16 — employer roles added to OrgRole enum."""

    def test_recruiter_exists(self):
        assert hasattr(OrgRole, "RECRUITER")
        assert OrgRole.RECRUITER.value == "recruiter"

    def test_hiring_manager_exists(self):
        assert hasattr(OrgRole, "HIRING_MANAGER")
        assert OrgRole.HIRING_MANAGER.value == "hiring_manager"

    def test_interviewer_exists(self):
        assert hasattr(OrgRole, "INTERVIEWER")
        assert OrgRole.INTERVIEWER.value == "interviewer"

    def test_role_hierarchy_includes_employer_roles(self):
        assert OrgRole.RECRUITER in ROLE_HIERARCHY
        assert OrgRole.HIRING_MANAGER in ROLE_HIERARCHY
        assert OrgRole.INTERVIEWER in ROLE_HIERARCHY

    def test_hiring_manager_outranks_recruiter(self):
        assert ROLE_HIERARCHY[OrgRole.HIRING_MANAGER] < ROLE_HIERARCHY[OrgRole.RECRUITER]

    def test_recruiter_outranks_interviewer(self):
        assert ROLE_HIERARCHY[OrgRole.RECRUITER] < ROLE_HIERARCHY[OrgRole.INTERVIEWER]

    def test_admin_outranks_hiring_manager(self):
        assert ROLE_HIERARCHY[OrgRole.ADMIN] < ROLE_HIERARCHY[OrgRole.HIRING_MANAGER]


class TestOrgType:
    """§16 — org_type column on Organization."""

    def test_org_has_org_type_column(self):
        from app.models.organization import Organization

        assert "org_type" in Organization.__table__.columns

    def test_org_type_default_is_school(self):
        col = __import__("app.models.organization", fromlist=["Organization"]).Organization.__table__.columns["org_type"]
        assert col.server_default is not None
        assert "school" in str(col.server_default.arg)
