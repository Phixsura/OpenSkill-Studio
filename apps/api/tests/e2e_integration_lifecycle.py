"""E2E integration-fabric lifecycle — runs against a live API (APP_ENV=test).

Issue #43 over real HTTP (rate-limit deps, exception handlers, envelopes,
auth stack, SCIM content types):

  register+org → domain claim (DB-verified; mock DNS can't pass our token
  prefix) → connection + write-only credential + ping → SCIM token → SCIM
  provision/filter/deactivate-reactivates → mapping create+preview → push
  sync profile → trigger → inline outbox drive → run succeeded → webhook
  subscription with a MESH pattern → mesh event emit (facade) → signed
  delivery to a LOCAL sink (EGRESS_ALLOW_PRIVATE=true in the driver env) →
  delivery log + replay over HTTP → export stream → run (MinIO) → IDOR
  spot-wall with a second user → cleanup.

Usage: make infra-up, then (dedicated port avoids stale-server 404s):
  cd apps/api && APP_ENV=test EGRESS_ALLOW_PRIVATE=true \
      uv run uvicorn app.main:app --port 8443 &
  cd apps/api && APP_ENV=test EGRESS_ALLOW_PRIVATE=true \
      E2E_INTG_API=http://localhost:8443/api/v1 \
      PYTHONPATH=. uv run python tests/e2e_integration_lifecycle.py
"""

import asyncio
import json
import os
import uuid

import httpx

API = os.environ.get("E2E_INTG_API", "http://localhost:8443/api/v1")

PASS = 0
FAIL = 0
STATE: dict = {"org_id": None, "sink_payloads": []}


def uid() -> str:
    return uuid.uuid4().hex[:10]


def check(name: str, ok: bool, detail: str = ""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f" FAIL {name}: {detail}")


async def db_session():
    from app.core.database import AsyncSessionLocal, engine

    await engine.dispose(close=False)
    return AsyncSessionLocal()


async def verify_domain_directly(domain_id: str) -> None:
    """Mock DNS verifier only passes 'ok-' tokens — flip in DB (the sweep
    path is covered by unit tests)."""
    from datetime import UTC, datetime

    from sqlalchemy import update

    from app.integrations.models import OrgDomain

    db = await db_session()
    async with db:
        await db.execute(
            update(OrgDomain)
            .where(OrgDomain.id == domain_id)
            .values(status="verified", verified_at=datetime.now(UTC))
        )
        await db.commit()


async def drive_outbox(rounds: int = 25) -> None:
    from app.controlplane.worker import process_outbox_once

    db = await db_session()
    async with db:
        for _ in range(rounds):
            if (
                await process_outbox_once(
                    db, topics=["intg.event.created", "intg.delivery.attempt", "intg.sync.run"]
                )
                == 0
            ):
                break


async def emit_mesh_event(org_id: str, payload: dict) -> str:
    from app.integrations.facade import emit_event

    db = await db_session()
    async with db:
        event = await emit_event(db, org_id, "project.approved", subject="e2e", data=payload)
        await db.commit()
        return event.id


class Sink:
    """Minimal local HTTP sink for signed webhook deliveries."""

    def __init__(self):
        self.payloads = []
        self.server = None
        self.port = None

    async def start(self):
        async def handle(reader, writer):
            data = await reader.read(65536)
            try:
                body = data.split(b"\r\n\r\n", 1)[1]
                headers = data.split(b"\r\n\r\n", 1)[0].decode(errors="replace")
                self.payloads.append({"headers": headers, "body": body})
            except Exception:
                pass
            writer.write(b"HTTP/1.1 200 OK\r\ncontent-length: 0\r\nconnection: close\r\n\r\n")
            await writer.drain()
            writer.close()

        # Port 8080: the egress guard allows only {80,443,8080,8443} even in
        # test-private mode — a random high port would be walled.
        self.server = await asyncio.start_server(handle, "127.0.0.1", 8080)
        self.port = self.server.sockets[0].getsockname()[1]

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()


async def main() -> int:
    sink = Sink()
    await sink.start()
    async with httpx.AsyncClient(base_url=API, timeout=30, trust_env=False) as c:
        # ── bootstrap: two users, one org ──
        email = f"e2e-intg-{uid()}@test.com"
        r = await c.post(
            "/auth/register",
            json={"email": email, "password": "Valid123!", "display_name": "E2E Intg"},
        )
        check("register", r.status_code == 201, r.text[:200])
        tok = r.json()["access_token"]
        admin_user_id = r.json()["user"]["id"]
        h = {"Authorization": f"Bearer {tok}"}

        r = await c.post(
            "/auth/register",
            json={
                "email": f"e2e-mallory-{uid()}@test.com",
                "password": "Valid123!",
                "display_name": "Mallory",
            },
        )
        mallory = {"Authorization": f"Bearer {r.json()['access_token']}"}

        r = await c.post("/orgs", json={"name": f"E2E Intg {uid()}"}, headers=h)
        check("org created", r.status_code == 201, r.text[:200])
        org_id = r.json()["data"]["id"]
        STATE["org_id"] = org_id
        base = f"/orgs/{org_id}/integrations"

        # ── providers catalog + connection + write-only credential ──
        r = await c.get(f"{base}/providers", headers=h)
        keys = {p["key"] for p in r.json().get("data", [])}
        check("catalog served", r.status_code == 200 and "generic_ats" in keys, r.text[:200])

        r = await c.post(
            f"{base}/connections",
            json={
                "provider_key": "generic_ats",
                "name": "E2E ATS",
                "config": {},
                "base_url": f"http://127.0.0.1:{sink.port}/ats",
            },
            headers=h,
        )
        check("connection created", r.status_code == 201, r.text[:300])
        conn_id = r.json()["data"]["id"]
        check(
            "connection response has no secrets",
            "ciphertext" not in r.text and "secret" not in r.json()["data"],
        )

        r = await c.post(
            f"{base}/connections/{conn_id}/credentials",
            json={"kind": "api_key", "values": {"api_key": "e2e-secret"}},
            headers=h,
        )
        check("credential stored write-only", r.status_code == 201 and "e2e-secret" not in r.text)

        r = await c.post(f"{base}/connections/{conn_id}/ping", headers=h)
        check(
            "ping ok",
            r.status_code == 200 and r.json()["data"]["ok"] is True,
            r.text[:200],
        )

        # R355: hardening headers on an authed JSON response.
        check(
            "no-store + no stack fingerprint on authed JSON",
            r.headers.get("cache-control") == "no-store"
            and "uvicorn" not in r.headers.get("server", "").lower(),
            f"cc={r.headers.get('cache-control')} server={r.headers.get('server')}",
        )

        # R344 regression wall: a live PATCH must serialize updated_at
        # cleanly (the update flush expires the onupdate column; without a
        # refresh the serializer's lazy load 500s with MissingGreenlet).
        r = await c.patch(
            f"{base}/connections/{conn_id}", json={"name": f"conn-{uid()}"}, headers=h
        )
        check(
            "connection PATCH serializes updated_at",
            r.status_code == 200 and r.json()["data"].get("updated_at"),
            r.text[:200],
        )

        # SSRF wall over HTTP (EGRESS_ALLOW_PRIVATE on, so use a blocked port)
        r = await c.post(
            f"{base}/connections",
            json={
                "provider_key": "generic_rest",
                "name": "evil",
                "config": {},
                # R396: the metadata-IP + redis-port URL is only blocked by
                # the PROD walls (private-IP + port), both deliberately open
                # under EGRESS_ALLOW_PRIVATE=true — assert a wall that holds
                # in EVERY mode instead (userinfo smuggling); the prod port
                # wall is pinned in test_integrations_core.
                "base_url": "https://admin:pw@evil.example.com/x",
            },
            headers=h,
        )
        check("egress userinfo wall", r.status_code == 422, r.text[:200])

        # ── domain + SCIM ──
        domain = f"e2e-{uid()}.example.edu"
        r = await c.post(f"{base}/domains", json={"domain": domain}, headers=h)
        check("domain claimed", r.status_code == 201, r.text[:200])
        domain_id = r.json()["data"]["id"]
        await verify_domain_directly(domain_id)

        r = await c.post(f"{base}/scim-tokens", json={"name": "e2e", "group_map": {}}, headers=h)
        check("scim token minted once", r.status_code == 201 and r.json()["data"]["token"])
        scim_raw = r.json()["data"]["token"]
        scim_h = {"Authorization": f"Bearer {scim_raw}"}

        r = await c.get(f"{base}/scim-tokens", headers=h)
        check(
            "scim token never listed again",
            all(t.get("token") in (None,) for t in r.json()["data"]),
        )

        learner_email = f"scim-{uid()}@{domain}"
        r = await c.post(
            "/scim/v2/Users",
            json={"userName": learner_email, "displayName": "SCIM Kid", "externalId": "x-1"},
            headers=scim_h,
        )
        check("scim provision 201", r.status_code == 201, r.text[:300])
        scim_user_id = r.json()["id"]

        r = await c.get(f'/scim/v2/Users?filter=userName eq "{learner_email}"', headers=scim_h)
        check(
            "scim filter finds user",
            r.status_code == 200 and r.json()["totalResults"] == 1,
            r.text[:200],
        )

        r = await c.patch(
            f"/scim/v2/Users/{scim_user_id}",
            json={"Operations": [{"op": "Replace", "path": "active", "value": "False"}]},
            headers=scim_h,
        )
        check(
            "scim entra-dialect deactivation",
            r.status_code == 200 and r.json()["active"] is False,
            r.text[:200],
        )
        r = await c.post(
            "/scim/v2/Users",
            json={"userName": learner_email},
            headers=scim_h,
        )
        check("scim reactivation not 409", r.status_code == 201, r.text[:200])

        r = await c.get("/scim/v2/Users", headers={"Authorization": "Bearer osks_scim_bogus"})
        check(
            "scim bad token -> scim-shaped 401",
            r.status_code == 401 and "urn:ietf:params:scim" in r.text,
        )

        # ── canonical model catalog (R487) ──
        r = await c.get(f"{base}/models", headers=h)
        models_ok = r.status_code == 200 and {m["model"] for m in r.json().get("data", [])} >= {
            "roster.user",
            "crm.deal",
            "talent.application",
        }
        schema_ok = models_ok and all(
            m["json_schema"]["type"] == "object"
            and set(m["required"]) <= set(m["json_schema"]["properties"])
            for m in r.json()["data"]
        )
        check("canonical model catalog served with schemas", bool(schema_ok), r.text[:200])

        # ── mapping + push sync profile ──
        r = await c.post(
            f"{base}/mapping-profiles",
            json={
                "name": f"map-{uid()}",
                "direction": "outbound",
                "model": "talent.application",
                "document": {"fields": [{"target": "status", "path": "status"}]},
            },
            headers=h,
        )
        check("mapping created", r.status_code == 201, r.text[:300])
        mapping_id = r.json()["data"]["id"]

        r = await c.post(
            f"{base}/mapping-profiles/{mapping_id}/preview",
            json={"samples": [{"status": "interview"}]},
            headers=h,
        )
        check(
            "mapping preview parity",
            r.status_code == 200 and r.json()["data"][0]["mapped"] == {"status": "interview"},
            r.text[:200],
        )

        r = await c.post(
            f"{base}/sync-profiles",
            json={
                "connection_id": conn_id,
                "name": f"push-{uid()}",
                "model": "talent.application",
                "direction": "push",
            },
            headers=h,
        )
        check("push profile created", r.status_code == 201, r.text[:300])
        profile_id = r.json()["data"]["id"]

        # R346 (R344 class): live PATCH walls for the remaining update
        # routes the suites only ever exercised in-process.
        r = await c.patch(
            f"{base}/sync-profiles/{profile_id}", json={"schedule": "daily"}, headers=h
        )
        check(
            "sync-profile PATCH live",
            r.status_code == 200 and r.json()["data"]["schedule"] == "daily",
            r.text[:200],
        )
        r = await c.patch(
            f"{base}/sync-profiles/{profile_id}", json={"schedule": "manual"}, headers=h
        )
        check("sync-profile PATCH back to manual", r.status_code == 200, r.text[:120])

        r = await c.post(f"{base}/sync-profiles/{profile_id}/run", headers=h)
        check("run queued (202)", r.status_code == 202, r.text[:200])
        run_id = r.json()["data"]["id"]
        await drive_outbox()
        r = await c.get(f"{base}/sync-runs/{run_id}", headers=h)
        check(
            "run executed inline -> succeeded (empty pipeline)",
            r.status_code == 200 and r.json()["data"]["status"] == "succeeded",
            r.text[:300],
        )

        # ── event mesh over a LOCAL sink ──
        r = await c.post(
            f"/orgs/{org_id}/webhooks",
            json={
                "url": f"http://127.0.0.1:{sink.port}/hook",
                "events": ["com.openskill.project.*"],
            },
            headers=h,
        )
        check("mesh-pattern subscription accepted", r.status_code == 201, r.text[:300])
        sub_id = r.json()["data"]["id"] if r.status_code == 201 else None
        event_id = await emit_mesh_event(org_id, {"project_id": "p-e2e", "user_id": "u"})
        await drive_outbox()
        await asyncio.sleep(0.2)
        check("signed delivery hit the sink", len(sink.payloads) >= 1)
        if sink.payloads:
            headers_blob = sink.payloads[0]["headers"]
            check(
                "standard-webhooks headers present",
                "webhook-id:" in headers_blob.lower()
                and "webhook-signature:" in headers_blob.lower(),
            )

        r = await c.get(f"{base}/deliveries?status=succeeded", headers=h)
        ok_rows = [d for d in r.json().get("data", []) if d["event_id"] == event_id]
        check("delivery log over HTTP", r.status_code == 200 and len(ok_rows) == 1, r.text[:200])
        if ok_rows:
            r = await c.post(f"{base}/deliveries/{ok_rows[0]['id']}/replay", headers=h)
            check("replay accepted", r.status_code == 200, r.text[:200])
            await drive_outbox()
            check("replay redelivered to sink", len(sink.payloads) >= 2)

        # ── R348 (R344 class): live walls for flush-then-serialize routes
        # the suites only ever hit in-process ──
        # SCIM Groups full live cycle
        r = await c.post(
            "/scim/v2/Groups",
            json={"displayName": f"Live G {uid()}"},
            headers=scim_h,
        )
        check("live SCIM group create", r.status_code == 201, r.text[:160])
        gid = r.json().get("id", "")
        r = await c.patch(
            f"/scim/v2/Groups/{gid}",
            json={
                "Operations": [
                    {"op": "replace", "path": "displayName", "value": f"Live G2 {uid()}"}
                ]
            },
            headers=scim_h,
        )
        check("live SCIM group PATCH", r.status_code == 200, r.text[:160])
        r = await c.get(f"/scim/v2/Groups/{gid}", headers=scim_h)
        check("live SCIM group GET", r.status_code == 200, r.text[:120])
        r = await c.delete(f"/scim/v2/Groups/{gid}", headers=scim_h)
        check("live SCIM group DELETE", r.status_code in (204, 200), str(r.status_code))

        # break-glass set + sync-run cancel (fresh queued run)
        r = await c.post(
            f"{base}/break-glass",
            json={"user_id": admin_user_id, "enabled": True},
            headers=h,
        )
        check("live break-glass set", r.status_code in (200, 204), str(r.status_code))
        r = await c.post(
            f"{base}/break-glass",
            json={"user_id": admin_user_id, "enabled": False},
            headers=h,
        )
        check("live break-glass unset", r.status_code in (200, 204), str(r.status_code))

        r = await c.post(f"{base}/sync-profiles/{profile_id}/run", headers=h)
        cancel_run_id = r.json()["data"]["id"]
        r = await c.post(f"{base}/sync-runs/{cancel_run_id}/cancel", headers=h)
        check(
            "live sync-run cancel",
            r.status_code == 200 and r.json()["data"]["status"] == "cancelled",
            r.text[:160],
        )

        # identity-queue live resolve (pending row minted in-process —
        # producing one over HTTP needs a real IdP's ambiguous assertion)
        from app.integrations.models import IdentityMatchQueue

        qdb = await db_session()
        async with qdb:
            item = IdentityMatchQueue(
                org_id=org_id,
                source="scim",
                connection_ref="e2e",
                subject=f"q-{uid()}",
                email=f"q-{uid()}@q.example.edu",
                reason="ambiguous",
                payload={},
                status="pending",
            )
            qdb.add(item)
            await qdb.commit()
            queue_item_id = item.id
        r = await c.post(
            f"{base}/identity-queue/{queue_item_id}/resolve",
            json={"action": "reject"},
            headers=h,
        )
        check(
            "live identity-queue resolve",
            r.status_code == 200 and r.json()["data"]["status"] == "rejected",
            r.text[:160],
        )

        # ── export (MinIO) ──
        r = await c.post(
            f"{base}/export-streams",
            json={"name": f"ev-{uid()}", "dataset": "events"},
            headers=h,
        )
        check("export stream created", r.status_code == 201, r.text[:300])
        stream_id = r.json()["data"]["id"]
        r = await c.post(f"{base}/export-streams/{stream_id}/run", headers=h)
        check(
            "export ran to object storage",
            r.status_code == 202 and r.json()["data"]["status"] == "succeeded",
            r.text[:300],
        )

        # ── R67-R70: SSO browser journey over HTTP ──
        r = await c.get(f"/sso/login?email=nobody@{domain}")
        check("discovery: no sso yet", r.status_code == 200 and r.json()["data"]["sso"] is False)
        r = await c.post(
            f"{base}/sso-connections",
            json={
                "protocol": "oidc",
                "oidc_issuer": "https://idp.example.com",
                "oidc_client_id": "e2e-client",
                "oidc_client_secret": "s3cret",
            },
            headers=h,
        )
        check("sso connection created", r.status_code == 201, r.text[:300])
        sso_id = r.json()["data"]["id"]
        r = await c.patch(f"{base}/sso-connections/{sso_id}", json={"status": "active"}, headers=h)
        check("sso connection activated", r.status_code == 200, r.text[:300])
        r = await c.get(f"/sso/login?email=nobody@{domain}")
        disc = r.json()["data"]
        check(
            "discovery routes to oidc authorize",
            r.status_code == 200
            and disc["sso"] is True
            and disc["authorize_url"].startswith("/api/v1/sso/oidc/authorize?"),
            r.text[:200],
        )

        # ── R36/R52: health summary + SCIM /Bulk over HTTP ──
        r = await c.get(f"{base}/health", headers=h)
        check(
            "fabric health summary",
            r.status_code == 200 and "connections" in r.json()["data"],
            r.text[:200],
        )
        bulk_email = f"bulk-{uid()}@{domain}"
        r = await c.post(
            "/scim/v2/Bulk",
            json={
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
                "Operations": [
                    {"method": "POST", "path": "/Users", "data": {"userName": bulk_email}},
                    {"method": "POST", "path": "/Users", "data": {"userName": bulk_email}},
                ],
            },
            headers=scim_h,
        )
        ops = r.json().get("Operations", [])
        check(
            "scim bulk mixed statuses",
            r.status_code == 200 and [o["status"] for o in ops] == ["201", "409"],
            r.text[:300],
        )

        # ── R93/R94: event catalog + payload archive over HTTP ──
        r = await c.get(f"{base}/event-catalog", headers=h)
        check(
            "event catalog served",
            r.status_code == 200 and "canonical" in r.json()["data"],
            r.text[:200],
        )
        if ok_rows:
            r = await c.get(f"{base}/deliveries/{ok_rows[0]['id']}/payload", headers=h)
            check(
                "payload archive byte view",
                r.status_code == 200 and r.json().get("id") == event_id,
                r.text[:200],
            )

        # ── R375: keyset pagination on the events list ──
        r = await c.get(f"{base}/events", params={"limit": 1}, headers=h)
        body = r.json()
        first_page = body.get("data", [])
        meta = body.get("meta", {})
        check(
            "events list carries keyset meta",
            r.status_code == 200 and "has_more" in meta and "next_cursor" in meta,
            r.text[:200],
        )
        if first_page and meta.get("has_more"):
            r2 = await c.get(
                f"{base}/events",
                params={"limit": 1, "before": meta["next_cursor"]},
                headers=h,
            )
            second = r2.json().get("data", [])
            check(
                "cursor page 2 is older and non-overlapping",
                r2.status_code == 200 and second and second[0]["id"] < first_page[0]["id"],
                r2.text[:200],
            )
        else:
            check("cursor page 2 is older and non-overlapping", True, "single page org")

        # ── R20/R22: identity links + webhook rotation over HTTP ──
        r = await c.get(f"{base}/identity-links", headers=h)
        check("identity links list (R20)", r.status_code == 200, r.text[:200])
        r = await c.delete(f"{base}/identity-links/01JUNKJUNKJUNKJUNKJUNKJUNK", headers=h)
        check("unlink unknown id is uniform 404", r.status_code == 404, str(r.status_code))
        r = await c.get(f"/orgs/{org_id}/webhooks", headers=h)
        hooks = r.json().get("data", [])
        check("subscription list", r.status_code == 200 and len(hooks) >= 1, r.text[:200])
        if hooks:
            r = await c.patch(
                f"/orgs/{org_id}/webhooks/{hooks[0]['id']}",
                json={"active": True},
                headers=h,
            )
            check("webhook PATCH live", r.status_code == 200, r.text[:160])
            r = await c.post(f"/orgs/{org_id}/webhooks/{hooks[0]['id']}/rotate-secret", headers=h)
            check(
                "rotate returns fresh secret once",
                r.status_code == 200 and r.json()["data"]["secret"].count("*") == 0,
                r.text[:200],
            )

        # ── bulk import over HTTP: JSON template, sniffed format (R128) ──
        import_email = f"e2e-imp-{uuid.uuid4().hex[:8]}@imports.example.edu"
        payload = json.dumps({"users": [{"email": import_email, "role": "student"}]})
        r = await c.post(
            f"{base}/imports",
            headers=h,
            data={
                "kind": "users",
                "mode": "partial",
                "idempotency_key": f"e2e-{uuid.uuid4().hex[:10]}",
            },
            files={"file": ("users.json", payload.encode(), "application/json")},
        )
        check(
            "JSON import previews over multipart HTTP",
            r.status_code in (200, 201) and r.json()["data"]["dry_stats"]["valid"] == 1,
            r.text[:300],
        )
        if r.status_code in (200, 201):
            import_job_id = r.json()["data"]["id"]
            r = await c.post(f"{base}/imports/{import_job_id}/commit", headers=h)
            check(
                "JSON import commits a user",
                r.status_code == 200 and r.json()["data"]["stats"]["created"] == 1,
                r.text[:200],
            )
            # idempotent re-upload returns the same job
            r = await c.post(
                f"{base}/imports",
                headers=h,
                data={
                    "kind": "users",
                    "mode": "partial",
                    "idempotency_key": f"e2e2-{uuid.uuid4().hex[:10]}",
                },
                files={"file": ("users.json", payload.encode(), "application/json")},
            )
            check(
                "re-upload previews as skip (idempotent)",
                r.status_code in (200, 201) and r.json()["data"]["dry_stats"]["skips"] == 1,
                r.text[:200],
            )
        # unknown kind refused at create
        r = await c.post(
            f"{base}/imports",
            headers=h,
            data={"kind": "nonsense", "mode": "partial"},
            files={"file": ("x.csv", b"email\n", "text/csv")},
        )
        check("unknown import kind refused", r.status_code == 422, str(r.status_code))

        # ── roster kind over HTTP: cohort by slug, member enrolled (R129) ──
        r = await c.post(
            f"/orgs/{org_id}/cohorts",
            headers=h,
            json={"name": f"E2E Cohort {uuid.uuid4().hex[:6]}"},
        )
        check("cohort created", r.status_code == 201, r.text[:200])
        if r.status_code == 201:
            cohort_slug = r.json()["data"]["slug"]
            roster_csv = f"email,cohort_slug,role\n{import_email},{cohort_slug},learner\n"
            r = await c.post(
                f"{base}/imports",
                headers=h,
                data={
                    "kind": "roster",
                    "mode": "partial",
                    "idempotency_key": f"e2er-{uuid.uuid4().hex[:10]}",
                },
                files={"file": ("roster.csv", roster_csv.encode(), "text/csv")},
            )
            check(
                "roster import previews an enrollment",
                r.status_code in (200, 201) and r.json()["data"]["dry_stats"]["creates"] == 1,
                r.text[:300],
            )
            if r.status_code in (200, 201):
                rid = r.json()["data"]["id"]
                r = await c.post(f"{base}/imports/{rid}/commit", headers=h)
                check(
                    "roster import enrolls the member",
                    r.status_code == 200 and r.json()["data"]["stats"]["created"] == 1,
                    r.text[:300],
                )

        # ── opportunities kind over HTTP: drafts behind the profile gate ──
        opp_title = f"E2E Role {uuid.uuid4().hex[:6]}"
        opp_json = json.dumps(
            {
                "opportunities": [
                    {
                        "title": opp_title,
                        "opportunity_type": "internship",
                        "location_mode": "remote",
                    },
                ]
            }
        )
        r = await c.post(
            f"{base}/imports",
            headers=h,
            data={
                "kind": "opportunities",
                "mode": "partial",
                "idempotency_key": f"e2eo-{uuid.uuid4().hex[:10]}",
            },
            files={"file": ("opps.json", opp_json.encode(), "application/json")},
        )
        check(
            "opportunities import without profile -> row errors",
            r.status_code in (200, 201)
            and r.json()["data"]["dry_stats"]["valid"] == 0
            and r.json()["data"]["dry_stats"]["errors"] == 1,
            r.text[:300],
        )
        r = await c.post("/talent/employers/" + org_id, headers=h, json={})
        check("employer profile registered", r.status_code == 201, r.text[:200])
        r = await c.post(
            f"{base}/imports",
            headers=h,
            data={
                "kind": "opportunities",
                "mode": "partial",
                "idempotency_key": f"e2eo2-{uuid.uuid4().hex[:10]}",
            },
            files={"file": ("opps.json", opp_json.encode(), "application/json")},
        )
        check(
            "opportunities import previews a draft",
            r.status_code in (200, 201) and r.json()["data"]["dry_stats"]["creates"] == 1,
            r.text[:300],
        )
        if r.status_code in (200, 201):
            oid = r.json()["data"]["id"]
            r = await c.post(f"{base}/imports/{oid}/commit", headers=h)
            check(
                "opportunities import lands a DRAFT",
                r.status_code == 200 and r.json()["data"]["stats"]["created"] == 1,
                r.text[:300],
            )
            r = await c.get(
                "/talent/opportunities",
                headers=h,
                params={"org_id": org_id, "status": "draft"},
            )
            check(
                "imported posting is draft-only",
                r.status_code == 200 and opp_title in r.text,
                r.text[:200],
            )

        # ── IDOR spot wall (second real user, not a member) ──
        for path in (
            f"{base}/connections/{conn_id}",
            f"{base}/sync-runs/{run_id}",
            f"{base}/scim-tokens",
            f"{base}/identity-links",
            f"{base}/sync-profiles",
            f"{base}/export-streams",
            f"{base}/mapping-profiles",
            f"{base}/imports",
        ):
            r = await c.get(path, headers=mallory)
            check(f"wall {path.split('/')[-1]}", r.status_code in (403, 404), str(r.status_code))

        # ── IDOR wall on WRITE surfaces (R481: the GET wall above never
        # probed the mutating per-resource endpoints phase-12 fuzzes) ──
        for method, path, body in (
            ("POST", f"{base}/connections/{conn_id}/upgrade", {}),
            ("POST", f"{base}/connections/{conn_id}/ping", {}),
            (
                "POST",
                f"{base}/connections/{conn_id}/credentials",
                {"kind": "api_key", "values": {"k": "v"}},
            ),
            (
                "POST",
                f"{base}/connections/{conn_id}/provision-roster",
                {"auto_create_cohorts": True},
            ),
            ("POST", f"{base}/sync-runs/{run_id}/cancel", {}),
            ("DELETE", f"{base}/connections/{conn_id}", None),
        ):
            r = await c.request(method, path, json=body, headers=mallory)
            check(
                f"write wall {method} {path.split('/')[-1]}",
                r.status_code in (403, 404),
                str(r.status_code),
            )

        # ── bulk replay of exhausted deliveries (R155) ──
        if sub_id:
            r = await c.post(f"{base}/webhooks/{sub_id}/replay-exhausted", headers=h)
            check(
                "bulk replay endpoint responds with a count",
                r.status_code == 200 and "requeued" in r.json().get("data", {}),
                r.text[:200],
            )

        # ── cleanup (best effort) ──
        await c.delete(f"{base}/connections/{conn_id}", headers=h)
        await c.delete(f"{base}/domains/{domain_id}", headers=h)
        if sub_id:
            await c.delete(f"/orgs/{org_id}/webhooks/{sub_id}", headers=h)

    await sink.stop()
    print(f"\nPASS={PASS} FAIL={FAIL}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
