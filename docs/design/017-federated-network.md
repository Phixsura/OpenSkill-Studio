# ADR-017 — Federated OpenSkill Network: Cross-instance Registry, Credential Trust, Talent Mobility, Marketplace Federation and Inter-tenant Collaboration

**Status:** Accepted  
**Date:** 2026-10-27  
**Relates to:** ADR-009 (Skill Pack Registry), ADR-012 (Matching Engine), ADR-013 (Composers/Talent), ADR-014 (SaaS Commercialization), ADR-015 (Talent Graph), ADR-016 (Developer Platform), Issue #45

---

## Context

Once OpenSkill has a developer platform and stable protocol boundaries, the next leap is **federation**. Different schools, regional operators, enterprises or countries may run separate OpenSkill deployments for sovereignty, customization or operational reasons. They should still be able to selectively exchange trusted public components, credentials, opportunities and ecosystem intelligence without sharing private tenant databases.

Federation is **opt-in, policy-controlled and provenance-preserving**. Private user/tenant data is excluded by default.

---

## Decision

### Part A — Instance Identity & Peering

#### Entities

```
FederationInstance
  ├── id: ULID (local PK)
  ├── instance_uri: str(500) — canonical HTTPS base URL, globally unique
  ├── display_name: str(200)
  ├── description: text — nullable
  ├── logo_url: str(500) — nullable
  ├── software_version: str(40) — e.g. "0.42.0"
  ├── protocol_version: str(10) — e.g. "1.0"
  ├── public_key_pem: text — Ed25519 public key, PEM-encoded
  ├── key_id: str(64) — SHA-256 fingerprint of public key
  ├── key_rotated_at: timestamptz
  ├── previous_key_pem: text — nullable, retained for grace-period verification
  ├── previous_key_id: str(64) — nullable
  ├── trust_status: enum(pending, trusted, suspended, revoked)
  ├── metadata: JSONB — { region, jurisdiction, operator_name, contact_email, ... }
  ├── last_seen_at: timestamptz — nullable, updated on successful sync
  ├── last_sync_error: text — nullable
  ├── created_at: timestamptz
  ├── updated_at: timestamptz

LocalInstanceIdentity (singleton row, id = "self")
  ├── id: str — always "self"
  ├── instance_uri: str(500) — this deployment's canonical URL
  ├── display_name: str(200)
  ├── signing_key_pem: text — Ed25519 private key (encrypted at rest via APP_ENCRYPTION_KEY)
  ├── public_key_pem: text — corresponding public key
  ├── key_id: str(64) — fingerprint
  ├── key_generated_at: timestamptz
  ├── previous_signing_key_pem: text — nullable (encrypted)
  ├── previous_key_id: str(64) — nullable
  ├── previous_key_expires_at: timestamptz — nullable, grace period
  ├── protocol_version: str(10) — "1.0"
  ├── metadata: JSONB
  ├── created_at: timestamptz
  ├── updated_at: timestamptz
```

#### Indexes

```sql
CREATE UNIQUE INDEX uq_fed_instance_uri ON federation_instances(instance_uri);
CREATE INDEX ix_fed_instance_trust ON federation_instances(trust_status);
CREATE INDEX ix_fed_instance_key_id ON federation_instances(key_id);
```

#### Key Management

- **Algorithm**: Ed25519 (compact 32-byte keys, fast sign/verify, no parameter confusion)
- **Rotation**: Admin triggers rotation → new keypair generated → old key enters 30-day grace period → `previous_key_pem` populated → after grace, `previous_*` nulled
- **Verification order**: try `key_id` first; if no match and `previous_key_id` matches and `previous_key_expires_at > now()`, verify with previous key
- **Private key encryption**: AES-256-GCM with key derived from `APP_ENCRYPTION_KEY` env var via HKDF(SHA-256, info="federation-signing-key")

#### Peering Handshake

```
1. Admin A adds peer B's instance_uri
2. System fetches GET {B}/.well-known/openskill-federation
   → returns { instance_uri, display_name, public_key_pem, key_id,
               protocol_version, software_version, metadata }
3. Local creates FederationInstance(trust_status=pending)
4. Admin A sets trust policies → trust_status=trusted
5. (Optional) B reciprocates by adding A
```

#### Well-known Endpoint

```
GET /.well-known/openskill-federation
→ 200 {
    "instance_uri": "https://school-a.openskill.io",
    "display_name": "School A OpenSkill",
    "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...",
    "key_id": "sha256:abc123...",
    "protocol_version": "1.0",
    "software_version": "0.42.0",
    "metadata": { "region": "EU", "jurisdiction": "DE", ... },
    "supported_artifact_types": ["skill_pack","workflow_pack","credential","opportunity","marketplace_listing","ecosystem_observation"],
    "federation_endpoints": {
      "registry_sync": "/api/v1/federation/registry/sync",
      "credential_verify": "/api/v1/federation/credentials/verify",
      "opportunity_search": "/api/v1/federation/opportunities/search",
      "revocation_status": "/api/v1/federation/revocations/status"
    }
  }
```

---

### Part B — Federation Protocol & Signed Envelopes

#### Envelope Format

Every federated message is a **signed envelope** — a JSON structure with a detached Ed25519 signature:

```json
{
  "envelope_version": "1.0",
  "envelope_id": "01JBXYZ...",           // ULID, globally unique
  "envelope_type": "registry_artifact | credential_snapshot | opportunity | marketplace_listing | ecosystem_observation | revocation | demand_signal",
  "source_instance": "https://school-a.openskill.io",
  "source_key_id": "sha256:abc123...",
  "issued_at": "2026-10-27T10:00:00Z",
  "expires_at": "2026-11-27T10:00:00Z",  // nullable
  "payload": { ... },                     // type-specific
  "signature": "base64url(...)"           // Ed25519(signing_key, canonical_json(envelope without signature field))
}
```

#### Canonicalization

Signature is computed over `canonical_json(envelope_minus_signature)`:

- Keys sorted lexicographically at every nesting level
- No trailing commas, no whitespace
- UTF-8 encoded bytes
- Python: `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`

#### Envelope Types & Payloads

| Type                    | Payload Contents                                                                                                                                                     |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `registry_artifact`     | `{ artifact_type, artifact_id, name, version, description, content_hash, category, author, license, created_at, tags, dependencies }`                                |
| `credential_snapshot`   | `{ credential_type, holder_pseudonym_id, issuer_instance, issuer_org_name, skill_names, level, issued_at, expires_at, evidence_summary_hash, revocation_check_url }` |
| `opportunity`           | `{ opportunity_id, title, description, org_name, location, remote_ok, skills_required, compensation_range, application_url, closes_at }`                             |
| `marketplace_listing`   | `{ listing_id, artifact_type, artifact_id, price, currency, license_type, publisher, listing_url }`                                                                  |
| `ecosystem_observation` | `{ observation_type, category, data, observation_period, methodology, confidence }`                                                                                  |
| `revocation`            | `{ revocation_type, target_type, target_id, reason, revoked_at }`                                                                                                    |
| `demand_signal`         | `{ signal_type, skills, region, demand_level, observation_period }`                                                                                                  |

#### Verification Algorithm

```python
def verify_envelope(envelope: dict, peer: FederationInstance) -> bool:
    sig_b64 = envelope.pop("signature")
    sig_bytes = base64url_decode(sig_b64)
    canonical = canonical_json(envelope)

    # Try current key
    if envelope["source_key_id"] == peer.key_id:
        return ed25519_verify(peer.public_key_pem, canonical, sig_bytes)

    # Try previous key within grace period
    if (peer.previous_key_id
        and envelope["source_key_id"] == peer.previous_key_id
        and peer.previous_key_expires_at
        and peer.previous_key_expires_at > utcnow()):
        return ed25519_verify(peer.previous_key_pem, canonical, sig_bytes)

    return False
```

---

### Part C — Trust Registry & Policies

#### Entities

```
TrustPolicy
  ├── id: ULID
  ├── instance_id: FK(federation_instances) — the peer
  ├── artifact_type: enum(
  │     registry_artifact, credential, opportunity,
  │     marketplace_listing, ecosystem_observation, all)
  ├── action: enum(accept, mirror, reject)
  │     — accept: allow inbound; mirror: accept + re-serve locally; reject: drop
  ├── conditions: JSONB — nullable, e.g. { "categories": ["ai","design"], "min_version": "1.0" }
  ├── priority: int — lower wins on conflict
  ├── enabled: bool
  ├── created_by: FK(users) — admin who set this
  ├── created_at: timestamptz
  ├── updated_at: timestamptz
```

#### Indexes

```sql
CREATE UNIQUE INDEX uq_trust_policy_instance_type ON trust_policies(instance_id, artifact_type, priority);
CREATE INDEX ix_trust_policy_enabled ON trust_policies(enabled) WHERE enabled = true;
```

#### Policy Evaluation

```python
def evaluate_trust(peer_id: str, artifact_type: str, artifact: dict) -> str:
    """Returns 'accept' | 'mirror' | 'reject'."""
    policies = get_policies(peer_id, artifact_type, enabled=True, order_by=priority)
    if not policies:
        policies = get_policies(peer_id, "all", enabled=True, order_by=priority)

    for policy in policies:
        if matches_conditions(policy.conditions, artifact):
            return policy.action

    # Default deny — federation is opt-in
    return "reject"
```

#### Error Codes

| Code                        | HTTP | Description                                       |
| --------------------------- | ---- | ------------------------------------------------- |
| `PEER_NOT_TRUSTED`          | 403  | Peer instance not in trusted state                |
| `ARTIFACT_TYPE_REJECTED`    | 403  | Trust policy rejects this artifact type from peer |
| `POLICY_CONDITION_MISMATCH` | 403  | Artifact doesn't meet policy conditions           |
| `TRUST_POLICY_CONFLICT`     | 409  | Duplicate priority for same instance+type         |

---

### Part D — Cross-instance Registry Federation

#### Entities

```
FederatedArtifact
  ├── id: ULID (local)
  ├── source_instance_id: FK(federation_instances)
  ├── source_artifact_id: str(26) — original ID on remote
  ├── artifact_type: enum(skill_pack, workflow_pack, benchmark_suite, developer_app)
  ├── name: str(200)
  ├── version: str(20)
  ├── description: text
  ├── content_hash: str(64) — SHA-256
  ├── category: str(100)
  ├── author_name: str(200)
  ├── license_spdx: str(40) — nullable
  ├── tags: JSONB — array of strings
  ├── dependencies: JSONB — nullable
  ├── envelope_id: str(26) — ULID of the signed envelope that delivered this
  ├── envelope_signature: text — retained for audit
  ├── is_mirrored: bool — whether local copy of content exists
  ├── mirror_status: enum(pending, synced, failed, stale) — nullable
  ├── remote_deleted: bool — source sent revocation; local copy preserved
  ├── first_seen_at: timestamptz
  ├── last_synced_at: timestamptz
  ├── metadata: JSONB
```

#### Indexes

```sql
CREATE UNIQUE INDEX uq_fed_artifact_source ON federated_artifacts(source_instance_id, source_artifact_id, version);
CREATE INDEX ix_fed_artifact_type ON federated_artifacts(artifact_type);
CREATE INDEX ix_fed_artifact_category ON federated_artifacts(category);
CREATE INDEX ix_fed_artifact_name_trgm ON federated_artifacts USING gin(name gin_trgm_ops);
```

#### Sync Protocol

```
1. GET /api/v1/federation/registry/sync?since={iso_timestamp}&types=skill_pack,workflow_pack&cursor={cursor}
   Header: X-Federation-Instance: {instance_uri}
   Header: X-Federation-Signature: {signature_of_request_body}

2. Response (paginated signed envelopes):
   {
     "data": [ { envelope }, { envelope }, ... ],
     "meta": { "cursor": "...", "has_more": true, "total": 142 }
   }

3. Receiver verifies each envelope signature
4. Applies trust policy per artifact
5. Upserts FederatedArtifact rows
6. If policy = mirror, queues content download
```

#### Installation of Federated Artifacts

When a user installs a federated artifact:

1. Create local `SkillPack` / `WorkflowPack` with `source_type = "federation"`, `source_instance_id`, `source_artifact_id`
2. All local validation (import parity rules from R86) applies — federation doesn't bypass safety
3. Local provenance record created: `{ origin: "federation", instance: "...", original_id: "...", content_hash: "..." }`
4. Remote deletion sets `remote_deleted = true` on `FederatedArtifact` — already-installed local content is **never** destroyed

---

### Part E — Credential / Passport Verification

#### Entities

```
FederatedCredentialVerification
  ├── id: ULID
  ├── verifier_user_id: FK(users) — who requested verification
  ├── verifier_org_id: FK(organizations) — nullable
  ├── source_instance_id: FK(federation_instances)
  ├── credential_type: enum(certificate, skill_assessment, portfolio_endorsement, learning_path_completion)
  ├── holder_pseudonym_id: str(64) — privacy-preserving holder identifier
  ├── credential_envelope_id: str(26) — envelope ULID
  ├── credential_data: JSONB — verified credential snapshot (no raw evidence)
  ├── verification_status: enum(verified, invalid_signature, expired, revoked, unknown)
  ├── verified_at: timestamptz
  ├── revocation_checked_at: timestamptz — nullable
  ├── expires_at: timestamptz — nullable
  ├── created_at: timestamptz
```

#### Indexes

```sql
CREATE INDEX ix_fed_cred_verifier ON federated_credential_verifications(verifier_user_id);
CREATE INDEX ix_fed_cred_source ON federated_credential_verifications(source_instance_id);
CREATE INDEX ix_fed_cred_holder ON federated_credential_verifications(holder_pseudonym_id);
CREATE INDEX ix_fed_cred_status ON federated_credential_verifications(verification_status);
```

#### Verification Protocol

```
1. Holder on Instance A exports credential snapshot → signed envelope
2. Holder presents envelope to Instance B
3. Instance B:
   a. Verifies envelope signature against Instance A's public key
   b. Checks revocation: GET {A}/api/v1/federation/credentials/{credential_id}/status
   c. Stores FederatedCredentialVerification
   d. Returns verification result
```

#### Privacy Rules

- **No raw evidence**: Only summary hashes and metadata cross the wire. Raw project files, submissions, assessment rubrics stay on the issuing instance.
- **Pseudonym IDs**: Holder is identified by a one-way hash `SHA-256(instance_uri + user_id + purpose_salt)` — different per verifying instance to prevent cross-instance tracking.
- **Explicit consent**: Holder must trigger the export; no automated credential broadcast.

#### Revocation Check Endpoint

```
GET /api/v1/federation/credentials/{credential_id}/status
→ {
    "credential_id": "01JBXYZ...",
    "status": "active | revoked | expired",
    "revoked_at": null,
    "revocation_reason": null,
    "checked_at": "2026-10-27T10:00:00Z"
  }
```

---

### Part F — Talent Mobility & Account Linking

#### Entities

```
FederatedAccountLink
  ├── id: ULID
  ├── local_user_id: FK(users)
  ├── remote_instance_id: FK(federation_instances)
  ├── remote_pseudonym_id: str(64)
  ├── link_status: enum(pending, active, revoked)
  ├── linked_at: timestamptz — nullable
  ├── consent_scope: JSONB — { "share_credentials": true, "share_portfolio": false, ... }
  ├── last_sync_at: timestamptz — nullable
  ├── created_at: timestamptz
  ├── updated_at: timestamptz

PortabilityRecord
  ├── id: ULID
  ├── user_id: FK(users)
  ├── account_link_id: FK(federated_account_links)
  ├── record_type: enum(credential_export, portfolio_snapshot, skill_summary)
  ├── data_hash: str(64) — SHA-256 of exported data
  ├── envelope_id: str(26) — signed envelope ULID
  ├── exported_at: timestamptz
  ├── expires_at: timestamptz
  ├── revoked_at: timestamptz — nullable
```

#### Indexes

```sql
CREATE UNIQUE INDEX uq_account_link_user_instance ON federated_account_links(local_user_id, remote_instance_id);
CREATE INDEX ix_account_link_status ON federated_account_links(link_status);
CREATE INDEX ix_portability_user ON portability_records(user_id);
CREATE INDEX ix_portability_link ON portability_records(account_link_id);
```

#### Linking Flow

```
1. User on Instance A initiates "Link to Instance B"
2. A generates link request with pseudonym_id = SHA-256(A_uri + user_id + B_uri)
3. User authenticates on B (redirect / out-of-band code)
4. B creates reciprocal FederatedAccountLink
5. Both sides: link_status → active
6. User selects consent_scope (what to share)
```

#### Rules

- **No automatic identity merge**: Separate accounts remain separate; linking only enables selective data sharing
- **Consent-gated**: Each data type (credentials, portfolio, skills) requires explicit opt-in
- **Revocable**: User can revoke link at any time → sets `link_status = revoked`, future syncs stop

---

### Part G — Opportunity Federation

#### Entities

```
FederatedOpportunity
  ├── id: ULID (local)
  ├── source_instance_id: FK(federation_instances)
  ├── source_opportunity_id: str(26)
  ├── title: str(300)
  ├── description: text
  ├── org_name: str(200) — publishing org's display name
  ├── location: str(200) — nullable
  ├── remote_ok: bool
  ├── skills_required: JSONB — array of skill descriptors
  ├── compensation_range: JSONB — nullable, { min, max, currency, period }
  ├── application_url: str(500) — where candidates apply
  ├── closes_at: timestamptz — nullable
  ├── status: enum(active, closed, withdrawn)
  ├── envelope_id: str(26)
  ├── envelope_signature: text
  ├── first_seen_at: timestamptz
  ├── last_synced_at: timestamptz
  ├── metadata: JSONB
```

#### Indexes

```sql
CREATE UNIQUE INDEX uq_fed_opp_source ON federated_opportunities(source_instance_id, source_opportunity_id);
CREATE INDEX ix_fed_opp_status ON federated_opportunities(status);
CREATE INDEX ix_fed_opp_closes ON federated_opportunities(closes_at) WHERE status = 'active';
CREATE INDEX ix_fed_opp_skills ON federated_opportunities USING gin(skills_required);
```

#### Application Evidence Bundle

When a candidate on Instance B applies to an opportunity from Instance A:

```json
{
  "envelope_type": "application_bundle",
  "payload": {
    "opportunity_id": "...",
    "candidate_pseudonym_id": "...",
    "credential_snapshots": [ /* signed credential envelopes */ ],
    "portfolio_summary": { "items_count": 5, "top_skills": [...], "portfolio_url": "..." },
    "cover_message": "..."
  }
}
```

- Candidate controls exactly which credentials/portfolio items are included
- Employment decisions remain **human-controlled** — no automated accept/reject across federation

---

### Part H — Marketplace Federation

#### Entities

```
FederatedMarketplaceListing
  ├── id: ULID (local)
  ├── source_instance_id: FK(federation_instances)
  ├── source_listing_id: str(26)
  ├── artifact_type: enum(skill_pack, workflow_pack, developer_app)
  ├── artifact_id: str(26) — maps to FederatedArtifact.source_artifact_id
  ├── price_minor: bigint — price in minor currency units (cents)
  ├── currency: str(3) — ISO 4217
  ├── license_type: str(50)
  ├── publisher_name: str(200)
  ├── listing_url: str(500) — remote listing detail page
  ├── status: enum(active, suspended, delisted)
  ├── envelope_id: str(26)
  ├── first_seen_at: timestamptz
  ├── last_synced_at: timestamptz

FederatedEntitlementGrant
  ├── id: ULID
  ├── listing_id: FK(federated_marketplace_listings)
  ├── buyer_org_id: FK(organizations)
  ├── buyer_user_id: FK(users)
  ├── seller_instance_id: FK(federation_instances)
  ├── grant_envelope_id: str(26) — signed entitlement envelope
  ├── grant_status: enum(pending, active, expired, revoked)
  ├── settlement_reference: str(200) — external payment ref (v1: manual)
  ├── settlement_status: enum(pending, confirmed, disputed, refunded)
  ├── granted_at: timestamptz
  ├── expires_at: timestamptz — nullable
  ├── created_at: timestamptz
  ├── updated_at: timestamptz
```

#### Indexes

```sql
CREATE UNIQUE INDEX uq_fed_listing_source ON federated_marketplace_listings(source_instance_id, source_listing_id);
CREATE INDEX ix_fed_listing_type ON federated_marketplace_listings(artifact_type);
CREATE INDEX ix_fed_listing_status ON federated_marketplace_listings(status) WHERE status = 'active';
CREATE INDEX ix_fed_entitlement_buyer ON federated_entitlement_grants(buyer_org_id);
CREATE INDEX ix_fed_entitlement_status ON federated_entitlement_grants(grant_status);
```

#### Settlement (v1)

- Financial clearing is **external/manual** in v1
- `settlement_reference` records an external payment ID (Stripe, bank transfer, PO number)
- Admin marks `settlement_status` transitions
- All transitions are audit-logged
- Signed entitlement grant envelope proves the seller authorized the license

---

### Part I — Ecosystem Intelligence Federation

#### Entities

```
FederatedEcosystemObservation
  ├── id: ULID (local)
  ├── source_instance_id: FK(federation_instances)
  ├── source_observation_id: str(26)
  ├── observation_type: str(50) — e.g. "skill_demand", "tool_adoption", "benchmark_result"
  ├── category: str(100)
  ├── data: JSONB — observation payload
  ├── observation_period: JSONB — { start, end }
  ├── methodology: str(200) — nullable
  ├── confidence: float — 0.0 to 1.0 (CHECK constraint)
  ├── envelope_id: str(26)
  ├── status: enum(active, disputed, retracted)
  ├── first_seen_at: timestamptz
  ├── last_synced_at: timestamptz
```

#### Indexes

```sql
CREATE UNIQUE INDEX uq_fed_eco_source ON federated_ecosystem_observations(source_instance_id, source_observation_id);
CREATE INDEX ix_fed_eco_type ON federated_ecosystem_observations(observation_type);
CREATE INDEX ix_fed_eco_category ON federated_ecosystem_observations(category);
```

#### Provenance Rules

- **Source trust ≠ instance trust**: An observation from peer A about tool X reflects A's measurement; local instance preserves attribution
- **Conflicting observations remain visible**: If peer A says "React demand = high" and peer B says "React demand = medium", both are stored and surfaced with source labels — no automatic averaging
- **Status `disputed`**: Admin can mark an observation disputed with a reason; it's still visible but flagged

---

### Part J — Federated Search

#### Architecture

```
Local-first search with optional peer fan-out:
1. Query hits local indexes (FTS + trigram)
2. If federation_search_enabled:
   a. Fan out to up to MAX_PEER_FANOUT (default 5) trusted peers
   b. Per-peer timeout: 3s (configurable)
   c. Circuit breaker: after 3 consecutive failures, pause peer for 5 minutes
3. Merge results: local results first, then remote ordered by relevance
4. Cache remote results for SEARCH_CACHE_TTL (default 5 minutes)
```

#### Entities

```
FederationSearchCache
  ├── id: ULID
  ├── query_hash: str(64) — SHA-256 of normalized query
  ├── source_instance_id: FK(federation_instances)
  ├── results: JSONB
  ├── cached_at: timestamptz
  ├── expires_at: timestamptz

FederationCircuitBreaker
  ├── instance_id: FK(federation_instances) — PK
  ├── consecutive_failures: int
  ├── last_failure_at: timestamptz
  ├── opened_at: timestamptz — nullable (null = closed)
  ├── half_open_at: timestamptz — nullable
```

#### Search Endpoint

```
POST /api/v1/federation/search
{
  "query": "react native animation",
  "types": ["skill_pack", "opportunity"],
  "include_remote": true,
  "max_peers": 3,
  "timeout_ms": 3000
}
→ {
    "data": {
      "local_results": [...],
      "remote_results": [
        { "source_instance": "https://school-b.openskill.io", "results": [...] }
      ]
    },
    "meta": { "peers_queried": 3, "peers_responded": 2, "peers_timed_out": 1 }
  }
```

---

### Part K — Cross-instance Collaboration

#### Entities

```
FederationGrant
  ├── id: ULID
  ├── grantor_org_id: FK(organizations)
  ├── grantee_instance_id: FK(federation_instances)
  ├── grantee_pseudonym_id: str(64) — remote user's pseudonym
  ├── grant_type: enum(reviewer, instructor, client, observer)
  ├── resource_type: str(50) — e.g. "project", "cohort", "submission"
  ├── resource_id: str(26) — FK to the specific resource
  ├── permissions: JSONB — { "can_view": true, "can_comment": true, "can_grade": false }
  ├── status: enum(pending, active, expired, revoked)
  ├── invited_at: timestamptz
  ├── accepted_at: timestamptz — nullable
  ├── expires_at: timestamptz
  ├── revoked_at: timestamptz — nullable
  ├── created_at: timestamptz
  ├── updated_at: timestamptz
```

#### Indexes

```sql
CREATE INDEX ix_fed_grant_org ON federation_grants(grantor_org_id);
CREATE INDEX ix_fed_grant_grantee ON federation_grants(grantee_instance_id, grantee_pseudonym_id);
CREATE INDEX ix_fed_grant_resource ON federation_grants(resource_type, resource_id);
CREATE INDEX ix_fed_grant_status ON federation_grants(status) WHERE status = 'active';
```

#### Rules

- Grantee never becomes a full local tenant member — they operate through scoped federation grants
- Grant permissions are strictly a subset: no escalation possible
- All actions by federated users are audit-logged with `actor_type = "federated"` and source instance

---

### Part L — Revocation & Key Rotation

#### Entities

```
FederationRevocation
  ├── id: ULID
  ├── instance_id: FK(federation_instances) — nullable (self-issued revocations have no peer)
  ├── revocation_type: enum(credential, app, component_signature, instance_key)
  ├── target_type: str(50) — e.g. "certificate", "developer_app", "skill_pack_release"
  ├── target_id: str(26)
  ├── reason: text
  ├── revoked_at: timestamptz
  ├── envelope_id: str(26) — signed revocation envelope
  ├── processed: bool — whether local side has acted on it
  ├── processed_at: timestamptz — nullable
  ├── created_at: timestamptz
```

#### Indexes

```sql
CREATE UNIQUE INDEX uq_fed_revocation_target ON federation_revocations(target_type, target_id, instance_id);
CREATE INDEX ix_fed_revocation_unprocessed ON federation_revocations(processed) WHERE processed = false;
```

#### Key Rotation Protocol

```
1. Admin triggers key rotation on Instance A
2. A generates new Ed25519 keypair
3. Old key → previous_signing_key_pem, previous_key_expires_at = now + 30d
4. New key → signing_key_pem
5. A signs a "key_rotation" envelope with OLD key:
   { "new_key_id": "...", "new_public_key_pem": "...", "old_key_id": "...", "grace_expires": "..." }
6. A pushes key_rotation envelope to all trusted peers
7. Peers update their FederationInstance record for A
8. After 30 days, A nulls previous_* fields; peers can discard old key
```

#### Historical Verification

Envelopes already signed with the old key remain valid if `signature_verified_at` was recorded before the grace period expired. The `envelope_signature` stored on federated artifacts serves as the audit trail.

---

### Part M — Data Residency & Sovereignty

#### Entities

```
DataResidencyPolicy
  ├── id: ULID
  ├── org_id: FK(organizations) — nullable (null = instance-wide)
  ├── policy_type: enum(region_restrict, jurisdiction_restrict, retention_limit, cross_border_block)
  ├── artifact_types: JSONB — array of applicable types, or ["all"]
  ├── conditions: JSONB — { "allowed_regions": ["EU","US"], "blocked_jurisdictions": ["XX"], "max_retention_days": 365 }
  ├── enforcement: enum(block, warn, audit_only)
  ├── enabled: bool
  ├── created_by: FK(users)
  ├── created_at: timestamptz
  ├── updated_at: timestamptz
```

#### Indexes

```sql
CREATE INDEX ix_residency_org ON data_residency_policies(org_id);
CREATE INDEX ix_residency_enabled ON data_residency_policies(enabled) WHERE enabled = true;
```

#### Policy Hook

Before any federated data is accepted or sent:

```python
def check_residency(direction: str, peer: FederationInstance, artifact_type: str, org_id: str | None) -> PolicyResult:
    """direction: 'inbound' | 'outbound'"""
    policies = get_residency_policies(org_id, artifact_type, enabled=True)
    peer_region = peer.metadata.get("region")
    peer_jurisdiction = peer.metadata.get("jurisdiction")

    for policy in policies:
        if policy.policy_type == "region_restrict":
            if peer_region not in policy.conditions.get("allowed_regions", []):
                return PolicyResult(action=policy.enforcement, reason=f"Region {peer_region} not in allowlist")
        elif policy.policy_type == "cross_border_block":
            if peer_jurisdiction != local_jurisdiction():
                return PolicyResult(action=policy.enforcement, reason="Cross-border transfer blocked")

    return PolicyResult(action="allow")
```

---

### Part N — Abuse / Reputation

#### Entities

```
PeerReputationScore
  ├── instance_id: FK(federation_instances) — PK
  ├── total_envelopes_received: bigint
  ├── invalid_signatures: bigint
  ├── expired_envelopes: bigint
  ├── revocations_issued: bigint
  ├── policy_violations: bigint
  ├── spam_score: float — rolling average, 0.0 (clean) to 1.0 (spam)
  ├── last_incident_at: timestamptz — nullable
  ├── auto_suspended: bool — threshold-triggered
  ├── updated_at: timestamptz

PeerIncident
  ├── id: ULID
  ├── instance_id: FK(federation_instances)
  ├── incident_type: enum(invalid_signature, spam, policy_violation, revocation_flood, timeout_flood)
  ├── severity: enum(low, medium, high, critical)
  ├── description: text
  ├── envelope_id: str(26) — nullable
  ├── created_at: timestamptz
  ├── resolved_at: timestamptz — nullable
  ├── resolved_by: FK(users) — nullable
```

#### Indexes

```sql
CREATE INDEX ix_peer_incident_instance ON peer_incidents(instance_id);
CREATE INDEX ix_peer_incident_type ON peer_incidents(incident_type);
CREATE INDEX ix_peer_incident_unresolved ON peer_incidents(resolved_at) WHERE resolved_at IS NULL;
```

#### Auto-suspension Thresholds

```python
THRESHOLDS = {
    "invalid_signature_rate": 0.05,    # >5% invalid → suspend
    "spam_score": 0.8,                  # rolling spam score > 0.8 → suspend
    "revocation_flood": 100,            # >100 revocations in 1h → review
    "policy_violations_per_day": 10,    # >10/day → suspend
}
```

- **Instance/artifact operational trust only** — no opaque social-credit scoring of people
- Auto-suspension is reversible by admin review
- All incidents create audit log entries

---

### Part O — Federation Admin (Backend APIs)

All federation admin endpoints live under `/api/v1/federation/` and require `role >= admin`.

| Method | Path                                                | Description                                   |
| ------ | --------------------------------------------------- | --------------------------------------------- |
| GET    | `/federation/identity`                              | Get local instance identity                   |
| PUT    | `/federation/identity`                              | Update local display_name, metadata           |
| POST   | `/federation/identity/rotate-key`                   | Trigger key rotation                          |
| GET    | `/federation/peers`                                 | List peer instances                           |
| POST   | `/federation/peers`                                 | Add peer by instance_uri (triggers handshake) |
| GET    | `/federation/peers/{id}`                            | Peer detail + reputation                      |
| PATCH  | `/federation/peers/{id}`                            | Update trust_status                           |
| DELETE | `/federation/peers/{id}`                            | Remove peer                                   |
| GET    | `/federation/peers/{id}/trust-policies`             | List trust policies for peer                  |
| POST   | `/federation/peers/{id}/trust-policies`             | Create trust policy                           |
| PATCH  | `/federation/peers/{id}/trust-policies/{policy_id}` | Update policy                                 |
| DELETE | `/federation/peers/{id}/trust-policies/{policy_id}` | Delete policy                                 |
| GET    | `/federation/artifacts`                             | List federated artifacts (with filters)       |
| GET    | `/federation/artifacts/{id}`                        | Federated artifact detail                     |
| POST   | `/federation/sync`                                  | Trigger manual sync with peers                |
| GET    | `/federation/sync/status`                           | Sync health dashboard data                    |
| GET    | `/federation/revocations`                           | List revocations                              |
| GET    | `/federation/residency-policies`                    | List residency policies                       |
| POST   | `/federation/residency-policies`                    | Create residency policy                       |
| GET    | `/federation/search`                                | Federated search                              |
| GET    | `/federation/reputation`                            | Peer reputation overview                      |
| GET    | `/federation/incidents`                             | List peer incidents                           |
| PATCH  | `/federation/incidents/{id}`                        | Resolve incident                              |

---

### Part P — Protocol Conformance

#### Conformance Test Suite

```python
class FederationConformanceTests:
    """Fixture-based protocol conformance tests for interoperability."""

    FIXTURES_DIR = "tests/federation/fixtures/"

    # 1. Well-known endpoint returns valid schema
    # 2. Signed envelope can be verified with provided public key
    # 3. Canonical JSON is deterministic
    # 4. Key rotation preserves historical verification within grace period
    # 5. Revocation envelope invalidates prior credential
    # 6. Trust policy correctly filters artifacts by type and conditions
    # 7. Circuit breaker opens after N consecutive failures
    # 8. Residency policy blocks cross-border transfer
    # 9. Pseudonym IDs are deterministic for same (instance, user, peer) triple
    # 10. Envelope with tampered payload fails verification
    # 11. Expired envelope is rejected
    # 12. Unknown envelope_type is safely ignored (forward compat)
```

#### Fixture Format

```json
// tests/federation/fixtures/valid_registry_envelope.json
{
  "description": "Valid skill_pack registry envelope from peer",
  "input": {
    "envelope": { ... },
    "peer_public_key_pem": "..."
  },
  "expected": {
    "signature_valid": true,
    "artifact_type": "skill_pack",
    "trust_action": "accept"
  }
}
```

---

## API Response Examples

### Single Peer

```json
{
  "data": {
    "id": "01JBXYZ...",
    "instance_uri": "https://school-b.openskill.io",
    "display_name": "School B",
    "trust_status": "trusted",
    "protocol_version": "1.0",
    "key_id": "sha256:def456...",
    "last_seen_at": "2026-10-27T09:00:00Z",
    "reputation": {
      "total_envelopes": 1523,
      "invalid_signature_rate": 0.001,
      "spam_score": 0.02
    }
  }
}
```

### Federated Artifact List

```json
{
  "data": [
    {
      "id": "01JBXYZ...",
      "source_instance": "https://school-b.openskill.io",
      "artifact_type": "skill_pack",
      "name": "Advanced React Patterns",
      "version": "2.1.0",
      "content_hash": "sha256:abc...",
      "is_mirrored": true,
      "remote_deleted": false,
      "first_seen_at": "2026-10-20T08:00:00Z"
    }
  ],
  "meta": { "total": 42, "page": 1, "per_page": 20, "has_more": true }
}
```

### Credential Verification Result

```json
{
  "data": {
    "id": "01JBXYZ...",
    "credential_type": "certificate",
    "holder_pseudonym_id": "sha256:fed789...",
    "verification_status": "verified",
    "credential_data": {
      "skill_names": ["React", "TypeScript"],
      "level": "advanced",
      "issuer_org_name": "Code Academy Alpha",
      "issued_at": "2026-09-15T00:00:00Z"
    },
    "verified_at": "2026-10-27T10:05:00Z"
  }
}
```

---

## Error Codes (Federation-specific)

| Code                          | HTTP | Description                                          |
| ----------------------------- | ---- | ---------------------------------------------------- |
| `FEDERATION_DISABLED`         | 403  | Federation is not enabled on this instance           |
| `PEER_NOT_FOUND`              | 404  | Peer instance not registered                         |
| `PEER_NOT_TRUSTED`            | 403  | Peer exists but not in trusted state                 |
| `PEER_SUSPENDED`              | 403  | Peer auto-suspended due to reputation                |
| `INVALID_ENVELOPE_SIGNATURE`  | 422  | Envelope signature verification failed               |
| `ENVELOPE_EXPIRED`            | 422  | Envelope `expires_at` is in the past                 |
| `UNKNOWN_KEY_ID`              | 422  | `source_key_id` doesn't match any known key for peer |
| `ARTIFACT_TYPE_REJECTED`      | 403  | Trust policy rejects this artifact type              |
| `RESIDENCY_BLOCKED`           | 403  | Data residency policy prevents this exchange         |
| `CIRCUIT_BREAKER_OPEN`        | 503  | Peer circuit breaker is open (too many failures)     |
| `FEDERATION_SYNC_IN_PROGRESS` | 409  | Another sync is already running                      |
| `CREDENTIAL_REVOKED`          | 422  | Credential has been revoked by issuing instance      |
| `GRANT_EXPIRED`               | 403  | Federation collaboration grant has expired           |
| `GRANT_REVOKED`               | 403  | Federation collaboration grant was revoked           |
| `SETTLEMENT_PENDING`          | 402  | Marketplace entitlement awaits settlement            |
| `SELF_PEERING_FORBIDDEN`      | 422  | Cannot add self as federation peer                   |

---

## Migration Plan

Single migration file: `federation01_core_tables.py`

Tables created in order (respecting FK dependencies):

1. `local_instance_identity`
2. `federation_instances`
3. `trust_policies`
4. `federated_artifacts`
5. `federated_credential_verifications`
6. `federated_account_links`
7. `portability_records`
8. `federated_opportunities`
9. `federated_marketplace_listings`
10. `federated_entitlement_grants`
11. `federated_ecosystem_observations`
12. `federation_grants`
13. `federation_revocations`
14. `data_residency_policies`
15. `peer_reputation_scores`
16. `peer_incidents`
17. `federation_search_cache`
18. `federation_circuit_breakers`

---

## Implementation Phases

### Phase 1 — Foundation (Parts A, B, C, L)

- Instance identity with Ed25519 signing
- Signed envelope protocol
- Trust registry and policies
- Key rotation and revocation
- Well-known endpoint
- Conformance test fixtures

### Phase 2 — Registry Federation (Part D)

- Cross-instance artifact discovery and sync
- Mirror support
- Federated installation with local provenance

### Phase 3 — Credentials & Talent (Parts E, F)

- Credential verification across instances
- Account linking and portability records
- Pseudonym-based privacy

### Phase 4 — Opportunities & Marketplace (Parts G, H)

- Opportunity federation and application bundles
- Marketplace listing sync
- Entitlement grants and settlement tracking

### Phase 5 — Intelligence & Search (Parts I, J)

- Ecosystem observation exchange
- Federated search with circuit breakers
- Search caching

### Phase 6 — Collaboration & Governance (Parts K, M, N, O, P)

- Cross-instance collaboration grants
- Data residency policies
- Peer reputation and abuse tracking
- Admin APIs
- Protocol conformance suite
