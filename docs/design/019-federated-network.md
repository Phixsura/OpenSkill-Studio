# ADR-019 — Federated OpenSkill Network

**Status:** Accepted  
**Date:** 2026-11-01  
**Relates to:** ADR-016 (Developer Platform), ADR-017 (AI Trust & Safety), ADR-018 (Global Operations), Issue #45

## Context

Independent OpenSkill deployments run across schools, regional operators, enterprises, and countries for sovereignty, customization, or operational reasons. They need to selectively exchange trusted public components, credentials, opportunities, and ecosystem intelligence without sharing private tenant databases.

## Decision

### Architecture

Federation code lives in the product layer (`app/models/federation.py`, `app/services/federation_*.py`) rather than a separate package, since it's a cross-cutting protocol layer integrated directly into the existing model and service structure.

### Core Protocol (Parts A–C, L)

- **Instance Identity**: Ed25519 keypairs with rotating signing keys, public metadata, software/protocol version
- **Crypto**: Canonical JSON signing, envelope verification, key ID computation
- **Trust Registry**: Peer instance management with trust policies (accept/reject/quarantine)
- **Revocation**: Key rotation, revocation records, incident tracking

### Exchange Layer (Parts D–J, M)

- **Artifact Exchange** (D): Cross-instance registry for skill/workflow packs with manifest + checksum + signature
- **Credential Verification** (E): Verify credentials issued by remote instances
- **Talent Mobility** (F): Account links + portability records for cross-instance profiles
- **Opportunity Federation** (G): Publish opportunities to federated instances
- **Marketplace Federation** (H): Cross-instance marketplace listing exchange
- **Ecosystem Intelligence** (I): Observation exchange (benchmarks, trends)
- **Federated Search** (J): Cached cross-instance search results with TTL
- **Data Residency** (M): Per-org residency policies with allowed/blocked regions

### Governance Layer (Parts K, N, P)

- **Collaboration** (K): Cross-instance resource grants with permission allowlist + expiry
- **Abuse/Reputation** (N): Per-peer reputation scoring, incident reporting
- **Protocol Conformance** (P): Version compatibility checks, circuit breakers

### Key Design Decisions

1. **Loose coupling**: Federation models use loose string refs (not FKs) for cross-instance references
2. **Opt-in**: All federation is explicit — no silent data sharing
3. **Provenance**: Every federated artifact carries origin instance, checksum, and signature
4. **Resource ownership validation**: Grants validate the resource belongs to the granting org before sharing
5. **Circuit breakers**: Automatic failure detection with state tracking per peer
6. **Grant allowlists**: Resource types and permissions are validated against fixed allowlists

### Security

- User org membership validated on account links, credentials, and portability records
- Resource ownership validated before granting cross-instance access
- Peer instance existence validated before grant creation
- Permission and resource type allowlists prevent arbitrary access grants

## Consequences

- Independent deployments can exchange components and credentials with cryptographic trust
- Talent can move between instances with portable profiles and verified credentials
- Marketplace and opportunity federation enable cross-instance discovery
- Circuit breakers protect against unreliable peers
- Data residency policies enforce regional sovereignty requirements
