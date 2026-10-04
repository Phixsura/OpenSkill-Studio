"""Platform-wide experimentation & decision intelligence (ADR-017, issue #42).

One shared experimentation layer across learning, production, marketplace,
matching and ecosystem domains. Safety posture (ADR-017 §2): employment
decisions are never randomized, guardrail breach can only auto-PAUSE (there is
no auto-promote code path), no protected-attribute targeting, running specs
are immutable, and the exposure/audit trail is append-only.
"""
