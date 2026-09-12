"""SaaS commercialization control plane (Issue #27, ADR-014).

Hard boundary rules:
- Product code imports ONLY `app.controlplane.facade` (never internals).
- Control-plane code may import product MODELS (app/models/*) but never
  product SERVICES — with the single ADR-approved exception of the
  provisioning orchestrator (see services/provisioning.py).
"""
