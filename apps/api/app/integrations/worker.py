"""Integration fabric worker handlers (ADR-018 §3/§12).

Rides the controlplane transactional-outbox worker: handlers register on the
shared topic registry and MUST be idempotent. Tests drive them inline via
app.controlplane.worker.process_outbox_once(db).

P1 ships the registry hookup only; P2 (event mesh) registers
``intg.event.created`` fan-out here.
"""

from __future__ import annotations

import structlog

log = structlog.get_logger()

# Imported for side effects by app.controlplane.worker (handler registration).
# No handlers yet in P1 — the module existing (and being imported) is what P2
# builds on without re-plumbing the worker.
