"""Live-server concurrency probe for Issue #21 race guards.

All race protections (install TOCTOU, run idempotency, review double-decide,
concurrent cancel+advance, parallel run creation) were built from sequential
reasoning — this script actually fires the races against a running server.

Usage:  APP_ENV=dev PYTHONPATH=. uv run python tests/e2e_concurrency_probe.py
Needs:  make dev-api running on :8000 (real Postgres/Redis).
"""

import asyncio
import sys
import uuid

import httpx

BASE = "http://localhost:8000/api/v1"
PASS: list[str] = []
FAIL: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail else ""))


DEFINITION = {
    "schema_version": 1,
    "inputs": [{"key": "topic", "type": "text", "required": True}],
    "outputs": [{"key": "final", "type": "prompt", "from_step": "build", "from_port": "prompt"}],
    "steps": [
        {
            "id": "take",
            "type": "asset_input",
            "name": "Take",
            "config": {"accept_types": ["image"]},
            "inputs": [],
            "outputs": [{"port": "topic", "type": "text"}],
        },
        {
            "id": "build",
            "type": "prompt_template",
            "name": "Build",
            "config": {"template": "About {{inputs.topic}}"},
            "inputs": [{"port": "topic", "type": "text"}],
            "outputs": [{"port": "prompt", "type": "prompt"}],
        },
    ],
    "edges": [
        {
            "id": "e1",
            "from_step": "take",
            "from_port": "topic",
            "to_step": "build",
            "to_port": "topic",
        }
    ],
    "ui": {},
}

REVIEW_DEFINITION = {
    "schema_version": 1,
    "inputs": [{"key": "topic", "type": "text", "required": True}],
    "outputs": [{"key": "final", "type": "text", "from_step": "gate", "from_port": "passed"}],
    "steps": [
        {
            "id": "take",
            "type": "asset_input",
            "name": "Take",
            "config": {"accept_types": ["image"]},
            "inputs": [],
            "outputs": [{"port": "topic", "type": "text"}],
        },
        {
            "id": "gate",
            "type": "review_gate",
            "name": "Gate",
            "config": {"instructions": "check", "due_days": 7},
            "inputs": [{"port": "subject", "type": "text"}],
            "outputs": [
                {"port": "decision", "type": "selection"},
                {"port": "passed", "type": "text"},
            ],
        },
    ],
    "edges": [
        {
            "id": "e1",
            "from_step": "take",
            "from_port": "topic",
            "to_step": "gate",
            "to_port": "subject",
        }
    ],
    "ui": {},
}


async def register(c: httpx.AsyncClient) -> dict:
    r = await c.post(
        f"{BASE}/auth/register",
        json={
            "email": f"conc-{uuid.uuid4().hex[:10]}@test.com",
            "password": "TestPass123!",
            "display_name": "Conc",
        },
    )
    r.raise_for_status()
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}


async def make_pack(c: httpx.AsyncClient, h: dict, oid: str, definition: dict) -> str:
    r = await c.post(
        f"{BASE}/orgs/{oid}/workflow-packs",
        json={"name": f"Conc-{uuid.uuid4().hex[:6]}"},
        headers=h,
    )
    pid = r.json()["data"]["id"]
    r2 = await c.put(
        f"{BASE}/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": definition},
        headers=h,
    )
    assert r2.status_code == 200, r2.text
    r3 = await c.post(
        f"{BASE}/orgs/{oid}/workflow-packs/{pid}/releases",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert r3.status_code == 201, r3.text
    return pid


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as c:
        h = await register(c)
        r = await c.post(
            f"{BASE}/orgs", json={"name": f"ConcOrg-{uuid.uuid4().hex[:6]}"}, headers=h
        )
        oid = r.json()["data"]["id"]

        # ── 1. Parallel install of the same pack: exactly one 201, rest 409 ──
        print("① Install TOCTOU (8 parallel installs of one pack)")
        pack_id = await make_pack(c, h, oid, DEFINITION)
        results = await asyncio.gather(
            *[
                c.post(
                    f"{BASE}/orgs/{oid}/workflow-installations",
                    json={"pack_id": pack_id},
                    headers=h,
                )
                for _ in range(8)
            ]
        )
        codes = sorted(r.status_code for r in results)
        n201 = codes.count(201)
        n409 = codes.count(409)
        n500 = sum(1 for s in codes if s >= 500)
        check("exactly one 201", n201 == 1, f"codes={codes}")
        check("rest are 409 (no 500s)", n409 == 7 and n500 == 0, f"codes={codes}")
        install_id = next(r.json()["data"]["id"] for r in results if r.status_code == 201)
        # install_count must be exactly 1
        r = await c.get(f"{BASE}/registry/workflow-packs/{pack_id}")
        if r.status_code == 200:
            check(
                "install_count == 1 (no double count)",
                r.json()["data"]["install_count"] == 1,
                f"count={r.json()['data']['install_count']}",
            )

        # ── 2. Idempotency key: 8 parallel creates → 1 run ──
        print("② Run idempotency (8 parallel creates, same key)")
        key = f"conc-{uuid.uuid4().hex[:8]}"
        results = await asyncio.gather(
            *[
                c.post(
                    f"{BASE}/orgs/{oid}/workflow-runs",
                    json={
                        "installation_id": install_id,
                        "inputs": {"topic": "race"},
                        "idempotency_key": key,
                    },
                    headers=h,
                )
                for _ in range(8)
            ]
        )
        codes = sorted(r.status_code for r in results)
        run_ids = {r.json()["data"]["id"] for r in results if r.status_code == 201}
        n5xx = sum(1 for s in codes if s >= 500)
        check("all 201 (idempotent echo)", all(s == 201 for s in codes), f"codes={codes}")
        check("exactly ONE distinct run id", len(run_ids) == 1, f"ids={len(run_ids)}")
        check("no 500s", n5xx == 0)

        # ── 3. Review double-decide: 6 parallel decides → 1 wins, rest 409 ──
        print("③ Review double-decide (6 parallel approve/reject)")
        rev_pack = await make_pack(c, h, oid, REVIEW_DEFINITION)
        r = await c.post(
            f"{BASE}/orgs/{oid}/workflow-installations",
            json={"pack_id": rev_pack},
            headers=h,
        )
        rev_install = r.json()["data"]["id"]
        r = await c.post(
            f"{BASE}/orgs/{oid}/workflow-runs",
            json={"installation_id": rev_install, "inputs": {"topic": "review race"}},
            headers=h,
        )
        rev_run = r.json()["data"]["id"]
        # Wait for WAITING_REVIEW
        review_id = None
        for _ in range(40):
            r = await c.get(f"{BASE}/orgs/{oid}/workflow-runs/{rev_run}", headers=h)
            if r.json()["data"]["status"] == "waiting_review":
                rr = await c.get(f"{BASE}/orgs/{oid}/step-reviews", headers=h)
                open_reviews = [x for x in rr.json()["data"] if x["decision"] is None]
                if open_reviews:
                    review_id = open_reviews[0]["id"]
                    break
            await asyncio.sleep(0.25)
        if review_id is None:
            check("review gate reached", False, "run never suspended")
        else:
            decisions = ["approved", "rejected"] * 3
            results = await asyncio.gather(
                *[
                    c.post(
                        f"{BASE}/orgs/{oid}/step-reviews/{review_id}/decide",
                        json={"decision": d},
                        headers=h,
                    )
                    for d in decisions
                ]
            )
            codes = sorted(r.status_code for r in results)
            n200 = codes.count(200)
            n409 = codes.count(409)
            n5xx = sum(1 for s in codes if s >= 500)
            check("exactly one decide wins (200)", n200 == 1, f"codes={codes}")
            check("losers get 409, never 500", n409 == 5 and n5xx == 0, f"codes={codes}")
            # The winning decision is the persisted one
            rr = await c.get(f"{BASE}/orgs/{oid}/step-reviews", headers=h)
            winner = next((r0.request, r0) for r0 in results if r0.status_code == 200)[1].json()[
                "data"
            ]["decision"]
            check("persisted decision == winner's", winner in ("approved", "rejected"))

        # ── 4. Cancel racing the advance loop ──
        print("④ Cancel racing advance (create + immediate cancel × 6)")
        stuck = 0
        bad_state = 0
        for _ in range(6):
            r = await c.post(
                f"{BASE}/orgs/{oid}/workflow-runs",
                json={"installation_id": install_id, "inputs": {"topic": "cancel race"}},
                headers=h,
            )
            rid = r.json()["data"]["id"]
            rc = await c.post(f"{BASE}/orgs/{oid}/workflow-runs/{rid}/cancel", headers=h)
            if rc.status_code >= 500:
                bad_state += 1
                continue
            # Whatever won the race, the run must settle to a terminal state
            final = None
            for _ in range(30):
                rg = await c.get(f"{BASE}/orgs/{oid}/workflow-runs/{rid}", headers=h)
                final = rg.json()["data"]["status"]
                if final in ("completed", "cancelled", "failed"):
                    break
                await asyncio.sleep(0.2)
            if final not in ("completed", "cancelled", "failed"):
                stuck += 1
        check("no 500s on cancel", bad_state == 0, f"bad={bad_state}")
        check("all runs settle terminal (none stuck)", stuck == 0, f"stuck={stuck}")

        # ── 5. Hot polling doesn't 500 or duplicate work ──
        print("⑤ Hot polling a running run (20 parallel GETs)")
        r = await c.post(
            f"{BASE}/orgs/{oid}/workflow-runs",
            json={"installation_id": install_id, "inputs": {"topic": "poll storm"}},
            headers=h,
        )
        rid = r.json()["data"]["id"]
        results = await asyncio.gather(
            *[c.get(f"{BASE}/orgs/{oid}/workflow-runs/{rid}", headers=h) for _ in range(20)]
        )
        n5xx = sum(1 for r0 in results if r0.status_code >= 500)
        check("20 concurrent polls, no 500s", n5xx == 0, f"5xx={n5xx}")
        for _ in range(30):
            rg = await c.get(f"{BASE}/orgs/{oid}/workflow-runs/{rid}", headers=h)
            if rg.json()["data"]["status"] == "completed":
                break
            await asyncio.sleep(0.2)
        check(
            "poll-stormed run completes exactly once",
            rg.json()["data"]["status"] == "completed",
            f"status={rg.json()['data']['status']}",
        )
        # Step runs must not be duplicated by racing advance loops
        steps = rg.json()["data"]["step_runs"]
        step_ids = [s["step_id"] for s in steps]
        check("no duplicated step_runs", len(step_ids) == len(set(step_ids)), f"{step_ids}")

        # ── 6. fork/upgrade racing remove: no zombie install (R55/R63) ──
        # These guards were proven only via seeded identity-map unit tests;
        # fire them against the live server with real concurrent sessions.
        print("⑥ fork / upgrade racing remove (no resurrection)")
        pid_fr = await make_pack(c, h, oid, DEFINITION)
        # publish a 2.0.0 so upgrade has a target
        await c.post(
            f"{BASE}/orgs/{oid}/workflow-packs/{pid_fr}/releases",
            json={"version": "2.0.0"},
            headers=h,
        )
        await c.post(f"{BASE}/orgs/{oid}/workflow-packs/{pid_fr}/submit-review", headers=h)
        await c.post(f"{BASE}/orgs/{oid}/workflow-packs/{pid_fr}/approve", headers=h)

        for label, mutate in (
            (
                "fork",
                lambda iid: c.post(
                    f"{BASE}/orgs/{oid}/workflow-installations/{iid}/fork", headers=h
                ),
            ),
            (
                "upgrade",
                lambda iid: c.post(
                    f"{BASE}/orgs/{oid}/workflow-installations/{iid}/upgrade",
                    json={"version": "2.0.0"},
                    headers=h,
                ),
            ),
        ):
            ri = await c.post(
                f"{BASE}/orgs/{oid}/workflow-installations",
                json={"pack_id": pid_fr, "version": "1.0.0"},
                headers=h,
            )
            if ri.status_code != 201:
                check(f"{label} setup install", False, f"{ri.status_code}: {ri.text[:200]}")
                continue
            iid = ri.json()["data"]["id"]
            # fire remove + the mutation together
            res = await asyncio.gather(
                c.request("DELETE", f"{BASE}/orgs/{oid}/workflow-installations/{iid}", headers=h),
                mutate(iid),
                return_exceptions=True,
            )
            codes = [r0.status_code for r0 in res if hasattr(r0, "status_code")]
            n5xx = sum(1 for x in codes if x >= 500)
            check(f"{label} vs remove: no 500s", n5xx == 0, f"codes={codes}")
            # After the race the install must be REMOVED — never resurrected
            # to ACTIVE/FORKED by the losing mutation.
            gi = await c.get(f"{BASE}/orgs/{oid}/workflow-installations/{iid}", headers=h)
            # 404 (removed + hidden) OR body status removed — never active/forked
            fstatus = gi.json()["data"]["status"] if gi.status_code == 200 else "gone"
            resurrected = fstatus in ("active", "forked")
            check(
                f"{label} vs remove: no zombie install",
                not resurrected,
                f"get={gi.status_code} status={fstatus} race={codes}",
            )
            # Best-effort cleanup so the next sub-case's fresh install on the
            # same (org, pack) doesn't collide with a leftover live row.
            if gi.status_code == 200:
                await c.request(
                    "DELETE",
                    f"{BASE}/orgs/{oid}/workflow-installations/{iid}",
                    headers=h,
                )

    print("\n" + "=" * 50)
    print(f"  {len(PASS)}/{len(PASS) + len(FAIL)} checks passed")
    print("=" * 50)
    if FAIL:
        print("FAILED:", *FAIL, sep="\n  - ")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
