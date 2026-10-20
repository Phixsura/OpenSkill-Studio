"""R596: access-grant audit invariant guard.

Every fabric code path that creates an OrgMember (grants a user access to an
organization) must leave a compliance-audit trail — whether per-event
(SCIM lifecycle, SSO JIT: system actor) or per-operation (bulk import
commit, NRPS sync: user actor). R592-R595 closed these one at a time; this
guard fails if a NEW OrgMember(...) construction appears in a module (or its
route layer) that records no audit, so the gap can't silently reopen.
"""

import pathlib
import re

APP = pathlib.Path(__file__).resolve().parent.parent / "app"
INTG = APP / "integrations"

# module (services file) -> where its audit lands (same file, or the route
# module that calls it). A creation site is covered if EITHER file mentions
# record_fabric_audit.
ROUTE_FOR = {
    "services/scim.py": ["services/scim.py"],
    "services/identity.py": ["services/identity.py"],
    "services/bulk_import.py": ["api/imports.py"],  # commit-level audit
    "services/roster.py": ["api/roster.py"],  # provision-level audit
}


def test_every_orgmember_creation_site_is_audited():
    offenders = []
    for f in INTG.rglob("*.py"):
        if "test" in f.name:
            continue
        text = f.read_text()
        if not re.search(r"\bOrgMember\(", text):
            continue
        rel = str(f.relative_to(INTG))
        # the file itself audits?
        if "record_fabric_audit" in text:
            continue
        # or a known route layer audits on its behalf?
        covered = False
        for route_rel in ROUTE_FOR.get(rel, []):
            rt = (INTG / route_rel)
            if rt.exists() and "record_fabric_audit" in rt.read_text():
                covered = True
                break
        if not covered:
            offenders.append(rel)
    assert not offenders, (
        f"OrgMember created without an audit trail in: {offenders} — "
        "every access grant must be audited (R592-R596). Add "
        "record_fabric_audit (system_actor=True for IdP-driven) or map the "
        "route layer in ROUTE_FOR."
    )
