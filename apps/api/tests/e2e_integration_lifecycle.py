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
            if await process_outbox_once(
                db, topics=["intg.event.created", "intg.delivery.attempt", "intg.sync.run"]
            ) == 0:
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

        # SSRF wall over HTTP (EGRESS_ALLOW_PRIVATE on, so use a blocked port)
        r = await c.post(
            f"{base}/connections",
            json={
                "provider_key": "generic_rest",
                "name": "evil",
                "config": {},
                "base_url": "https://169.254.169.254:6379/x",
            },
            headers=h,
        )
        check("egress port wall", r.status_code == 422, r.text[:200])

        # ── domain + SCIM ──
        domain = f"e2e-{uid()}.example.edu"
        r = await c.post(f"{base}/domains", json={"domain": domain}, headers=h)
        check("domain claimed", r.status_code == 201, r.text[:200])
        domain_id = r.json()["data"]["id"]
        await verify_domain_directly(domain_id)

        r = await c.post(
            f"{base}/scim-tokens", json={"name": "e2e", "group_map": {}}, headers=h
        )
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

        r = await c.get(
            f'/scim/v2/Users?filter=userName eq "{learner_email}"', headers=scim_h
        )
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

        # ── IDOR spot wall (second real user, not a member) ──
        for path in (
            f"{base}/connections/{conn_id}",
            f"{base}/sync-runs/{run_id}",
            f"{base}/scim-tokens",
        ):
            r = await c.get(path, headers=mallory)
            check(f"wall {path.split('/')[-1]}", r.status_code in (403, 404), str(r.status_code))

        # ── cleanup (best effort) ──
        await c.delete(f"{base}/connections/{conn_id}", headers=h)

    await sink.stop()
    print(f"\nPASS={PASS} FAIL={FAIL}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
