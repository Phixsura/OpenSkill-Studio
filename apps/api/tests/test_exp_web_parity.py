"""Web ↔ backend vocabulary parity for the Experiment Console (ADR-017).

The §106.7 law: web dropdown vocabularies are CI-pinned to the backend
constants — a silently divergent option list produces filters that 422 (or
worse, silently-empty lists). Parses apps/web experiments lib.ts and pins its
arrays to app/experiments/security.py, including the transition table.
"""

import re
from pathlib import Path

from app.experiments.models.decision import DECISIONS, PROMOTION_STATUSES
from app.experiments.security import (
    ANALYSIS_TYPES,
    EXPERIMENT_DOMAINS,
    EXPERIMENT_STATUSES,
    PROMOTION_TARGET_TYPES,
    RISK_CLASSES,
    SEQUENTIAL_METHODS,
    STATS_ENGINES,
    UNIT_TYPES,
)
from app.experiments.services.experiments import _ALLOWED

_LIB = (
    Path(__file__).resolve().parents[2]
    / "web" / "src" / "app" / "(dashboard)" / "dashboard" / "experiments" / "lib.ts"
)


def _web_array(name: str) -> set[str]:
    text = _LIB.read_text(encoding="utf-8")
    match = re.search(rf"export const {name} = \[(.*?)\] as const;", text, re.DOTALL)
    assert match, f"{name} not found in experiments lib.ts"
    return set(re.findall(r'"([a-z_]+)"', match.group(1)))


def test_web_vocabularies_match_backend():
    assert _web_array("EXPERIMENT_STATUSES") == set(EXPERIMENT_STATUSES)
    assert _web_array("EXPERIMENT_DOMAINS") == set(EXPERIMENT_DOMAINS)
    assert _web_array("UNIT_TYPES") == set(UNIT_TYPES)
    assert _web_array("RISK_CLASSES") == set(RISK_CLASSES)
    assert _web_array("STATS_ENGINES") == set(STATS_ENGINES)
    assert _web_array("SEQUENTIAL_METHODS") == set(SEQUENTIAL_METHODS)
    assert _web_array("ANALYSIS_TYPES") == set(ANALYSIS_TYPES)
    assert _web_array("DECISIONS") == set(DECISIONS)
    assert _web_array("PROMOTION_STATUSES") == set(PROMOTION_STATUSES)
    assert _web_array("PROMOTION_TARGET_TYPES") == set(PROMOTION_TARGET_TYPES)


def test_web_checklist_matches_backend():
    from app.experiments.security import (
        ETHICS_CHECKLIST_DOMAINS,
        ETHICS_CHECKLIST_KEY,
        LAUNCH_CHECKLIST_KEYS,
    )

    assert _web_array("LAUNCH_CHECKLIST_KEYS") == set(LAUNCH_CHECKLIST_KEYS)
    assert _web_array("ETHICS_CHECKLIST_DOMAINS") == set(ETHICS_CHECKLIST_DOMAINS)
    text = _LIB.read_text(encoding="utf-8")
    assert f'ETHICS_CHECKLIST_KEY = "{ETHICS_CHECKLIST_KEY}"' in text


def test_web_transition_table_matches_state_machine():
    text = _LIB.read_text(encoding="utf-8")
    match = re.search(
        r"export const ALLOWED_TRANSITIONS[^{]*\{(.*?)\n\};", text, re.DOTALL
    )
    assert match, "ALLOWED_TRANSITIONS not found in experiments lib.ts"
    web: dict[str, set[str]] = {}
    for status, targets in re.findall(r"(\w+): \[([^\]]*)\]", match.group(1)):
        web[status] = set(re.findall(r'"([a-z_]+)"', targets))
    assert web == {k: set(v) for k, v in _ALLOWED.items()}
