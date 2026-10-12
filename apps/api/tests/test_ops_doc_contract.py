"""R290 (R231 drift-guard class, docs edition): the operator-facing caps
table in docs/ops/integration-fabric-operations.md must match the code
constants — a cap change that skips the doc misleads the operators the
table exists for."""

from __future__ import annotations

import pathlib
import re

OPS_DOC = pathlib.Path(__file__).resolve().parents[3] / "docs/ops/integration-fabric-operations.md"


def _doc_caps() -> dict[str, int]:
    """Parse `| label | n | CODE |` rows from the caps table."""
    caps: dict[str, int] = {}
    for line in OPS_DOC.read_text().splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*`([A-Z_]+)`\s*\|", line)
        if m:
            caps[m.group(3)] = int(m.group(2))
    return caps


def test_ops_caps_table_matches_code():
    from app.integrations.models.scim import MAX_SCIM_TOKENS_PER_ORG
    from app.integrations.services.connections import MAX_CONNECTIONS_PER_ORG
    from app.integrations.services.domains import MAX_DOMAINS_PER_ORG
    from app.integrations.services.lti import (
        MAX_DEPLOYMENTS_PER_REGISTRATION,
        MAX_LTI_REGISTRATIONS_PER_ORG,
    )
    from app.integrations.services.sso_admin import MAX_SSO_CONNECTIONS_PER_ORG
    from app.integrations.services.sync_engine import MAX_SYNC_PROFILES_PER_ORG
    from app.integrations.services.warehouse import MAX_STREAMS_PER_ORG

    code = {
        "BREAK_GLASS_LIMIT": 2,  # literal in set_break_glass (pinned by test)
        "SCIM_TOKEN_LIMIT": MAX_SCIM_TOKENS_PER_ORG,
        "SSO_LIMIT_REACHED": MAX_SSO_CONNECTIONS_PER_ORG,
        "CONNECTION_LIMIT_REACHED": MAX_CONNECTIONS_PER_ORG,
        "EXPORT_LIMIT_REACHED": MAX_STREAMS_PER_ORG,
        "SYNC_PROFILE_LIMIT_REACHED": MAX_SYNC_PROFILES_PER_ORG,
        "LTI_REGISTRATION_LIMIT_REACHED": MAX_LTI_REGISTRATIONS_PER_ORG,
        "LTI_REGISTRATION_INVALID": MAX_DEPLOYMENTS_PER_REGISTRATION,
        "DOMAIN_LIMIT_REACHED": MAX_DOMAINS_PER_ORG,
    }
    doc = _doc_caps()
    assert doc, "caps table not found in the ops doc — heading or format moved"
    drift = {k: (doc.get(k), v) for k, v in code.items() if doc.get(k) != v}
    assert drift == {}, f"ops caps table drifted from code (doc, code): {drift}"
