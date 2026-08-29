#!/usr/bin/env python3
"""End-to-end smoke test against a running server.

Usage: PYTHONPATH=. python3 tests/e2e_smoke.py
Requires: uvicorn running on :8000 + Docker infra
"""

import json
import sys
import urllib.error
import urllib.request
import uuid

BASE = "http://localhost:8000/api/v1"
PASS = 0
FAIL = 0


def api(method, path, body=None, headers=None, expect=200):
    global PASS, FAIL
    url = f"{BASE}{path}"
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(req)
        raw = resp.read()
        # 204s carry an application/json content-type with an EMPTY body —
        # json.loads(b"") crashes. Parse only when there are bytes.
        result = (
            json.loads(raw)
            if raw and resp.headers.get("content-type", "").startswith("application/json")
            else {}
        )
        if resp.status == expect:
            PASS += 1
            return result
        else:
            FAIL += 1
            print(f"  ❌ {method} {path} → {resp.status} (expected {expect})")
            return result
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        if e.code == expect:
            PASS += 1
            return json.loads(body_text) if body_text else {}
        else:
            FAIL += 1
            print(f"  ❌ {method} {path} → {e.code} (expected {expect}): {body_text[:200]}")
            return {}


def section(name):
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")


def check(label, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")


# ════════════════════════════════════════════════════════
section("1. Health")
r = api("GET", "/health")
check("liveness ok", r.get("status") == "ok")

r = api("GET", "/health/ready")
check("readiness ok", r.get("status") in ("ok", "degraded"))
check("database ok", r.get("components", {}).get("database") == "ok")
check("redis ok", r.get("components", {}).get("redis") == "ok")

# ════════════════════════════════════════════════════════
section("2. Auth: Register + Login")
# Unique per run — a hardcoded address 409s (EMAIL_ALREADY_EXISTS) on every
# rerun against the shared dev DB.
email = f"smoke-{uuid.uuid4().hex[:10]}@example.com"
r = api(
    "POST",
    "/auth/register",
    {"email": email, "password": "Smoke123!", "display_name": "Smoke Test"},
    expect=201,
)
if not r.get("access_token"):
    # Already exists, login instead
    r = api("POST", "/auth/login", {"email": email, "password": "Smoke123!"})
token = r.get("access_token", "")
AUTH = {"Authorization": f"Bearer {token}"}
check("got access token", bool(token))
check("user role is student", r.get("user", {}).get("role") == "student")

# ════════════════════════════════════════════════════════
section("3. Auth: Me + Update + Sessions")
r = api("GET", "/auth/me", headers=AUTH)
check("/me returns user", r.get("data", {}).get("email") == email)

r = api(
    "PUT",
    "/auth/me",
    {"display_name": "Smoke Updated", "avatar_url": "https://img.com/a.jpg"},
    headers=AUTH,
)
check("update display_name", r.get("data", {}).get("display_name") == "Smoke Updated")
check("update avatar_url", r.get("data", {}).get("avatar_url") == "https://img.com/a.jpg")

r = api("GET", "/auth/sessions", headers=AUTH)
check("sessions list", isinstance(r.get("data"), list) and len(r["data"]) >= 1)

# ════════════════════════════════════════════════════════
section("4. Auth: Forgot password + Errors")
r = api("POST", "/auth/forgot-password", {"email": email}, expect=204)
check("forgot password 204", True)

r = api("POST", "/auth/forgot-password", {"email": "nobody@x.com"}, expect=204)
check("forgot nonexistent 204 (no leak)", True)

r = api("POST", "/auth/login", {"email": email, "password": "Wrong123!"}, expect=401)
check("wrong password 401", r.get("error", {}).get("code") == "INVALID_CREDENTIALS")

r = api("GET", "/auth/me", expect=401)
check("no token 401", True)

# ════════════════════════════════════════════════════════
section("5. Organizations")
org_name = f"Smoke Org {uuid.uuid4().hex[:6]}"
r = api("POST", "/orgs", {"name": org_name, "description": "E2E test"}, headers=AUTH, expect=201)
check("create org", r.get("data", {}).get("name") == org_name)
oid = r.get("data", {}).get("id", "")
check("creator is owner", r.get("data", {}).get("role") == "owner")

r = api("GET", "/orgs", headers=AUTH)
check("list orgs", any(o["id"] == oid for o in r.get("data", [])))

r = api("GET", f"/orgs/{oid}", headers=AUTH)
check("get org detail", r.get("data", {}).get("name") == org_name)

r = api("PUT", f"/orgs/{oid}", {"name": "Smoke Org Updated"}, headers=AUTH)
check("update org", r.get("data", {}).get("name") == "Smoke Org Updated")

r = api("GET", f"/orgs/{oid}/members", headers=AUTH)
check("list members", r.get("meta", {}).get("total") == 1)

# Invite link
r = api(
    "POST",
    f"/orgs/{oid}/invite-links",
    {"role": "student", "max_uses": 5},
    headers=AUTH,
    expect=201,
)
check("create invite link", bool(r.get("data", {}).get("code")))
link_code = r.get("data", {}).get("code", "")

r = api("GET", f"/orgs/{oid}/invite-links", headers=AUTH)
check("list invite links", len(r.get("data", [])) >= 1)

# Settings
r = api("PUT", f"/orgs/{oid}/settings", {"settings": {"max_members": 50}}, headers=AUTH)
check("update settings", True)

# ════════════════════════════════════════════════════════
section("6. Skills + Exercises + Grading")
r = api("POST", f"/orgs/{oid}/categories", {"name": "AI Skills"}, headers=AUTH, expect=201)
check("create category", r.get("data", {}).get("name") == "AI Skills")
cid = r.get("data", {}).get("id", "")

r = api("GET", f"/orgs/{oid}/categories", headers=AUTH)
check("list categories", len(r.get("data", [])) >= 1)

r = api(
    "POST",
    f"/orgs/{oid}/skills",
    {
        "category_id": cid,
        "name": "Prompt Engineering",
        "description": "Master prompts",
        "learning_content": "# Prompting\n\nLearn to write effective prompts.",
        "difficulty": "beginner",
        "tags": ["ai", "llm"],
        "estimated_minutes": 30,
    },
    headers=AUTH,
    expect=201,
)
check("create skill", r.get("data", {}).get("name") == "Prompt Engineering")
sid = r.get("data", {}).get("id", "")

r = api("GET", f"/orgs/{oid}/skills", headers=AUTH)
check("list skills", r.get("meta", {}).get("total") >= 1)

r = api("GET", f"/orgs/{oid}/skills?difficulty=beginner&tag=ai&q=Prompt", headers=AUTH)
check("filter skills", r.get("meta", {}).get("total") >= 1)

r = api("GET", f"/orgs/{oid}/skills/{sid}", headers=AUTH)
check("skill detail has content", r.get("data", {}).get("learning_content") is not None)

r = api("POST", f"/orgs/{oid}/skills/{sid}/publish", headers=AUTH)
check("publish skill", r.get("data", {}).get("status") == "published")

r = api("POST", f"/orgs/{oid}/skills/{sid}/unpublish", headers=AUTH)
check("unpublish skill", r.get("data", {}).get("status") == "draft")

# Exercise (MCQ)
r = api(
    "POST",
    f"/orgs/{oid}/skills/{sid}/exercises",
    {
        "title": "MCQ: Prompting",
        "description": "Pick the best",
        "type": "multiple_choice",
        "config": {
            "correct": ["b"],
            "options": [
                {"id": "a", "text": "Ignore context"},
                {"id": "b", "text": "Provide examples"},
            ],
            "explanation": "Few-shot prompting uses examples.",
        },
    },
    headers=AUTH,
    expect=201,
)
check("create MCQ exercise", r.get("data", {}).get("type") == "multiple_choice")
eid = r.get("data", {}).get("id", "")

# Exercise (Text)
r = api(
    "POST",
    f"/orgs/{oid}/skills/{sid}/exercises",
    {
        "title": "Text: Explain CoT",
        "description": "Write an explanation",
        "type": "text_answer",
        "config": {},
    },
    headers=AUTH,
    expect=201,
)
eid2 = r.get("data", {}).get("id", "")

r = api("GET", f"/orgs/{oid}/skills/{sid}/exercises", headers=AUTH)
check("list exercises", len(r.get("data", [])) >= 2)

# Submit correct MCQ
r = api(
    "POST",
    f"/orgs/{oid}/exercises/{eid}/attempts",
    {"answer": {"selected": ["b"]}},
    headers=AUTH,
    expect=201,
)
check("MCQ correct → auto-grade", r.get("data", {}).get("is_correct") is True)
check("MCQ score=100", r.get("data", {}).get("score") == 100)
check("MCQ graded_by=auto", r.get("data", {}).get("graded_by") == "auto")
check("MCQ feedback", r.get("data", {}).get("feedback") is not None)

# Submit wrong MCQ
r = api(
    "POST",
    f"/orgs/{oid}/exercises/{eid}/attempts",
    {"answer": {"selected": ["a"]}},
    headers=AUTH,
    expect=201,
)
check("MCQ wrong → score=0", r.get("data", {}).get("score") == 0)
check("MCQ wrong → is_correct=False", r.get("data", {}).get("is_correct") is False)

# Attempt history
r = api("GET", f"/orgs/{oid}/exercises/{eid}/attempts", headers=AUTH)
check("attempt history", len(r.get("data", [])) >= 2)

# Submit text answer
r = api(
    "POST",
    f"/orgs/{oid}/exercises/{eid2}/attempts",
    {"answer": {"text": "Chain of thought means..."}},
    headers=AUTH,
    expect=201,
)
check("text answer submitted", r.get("data", {}).get("score") is None)
aid = r.get("data", {}).get("id", "")

# Pending grading
r = api("GET", f"/orgs/{oid}/grading/pending", headers=AUTH)
check("pending grading list", len(r.get("data", [])) >= 1)

# Manual grade
r = api(
    "POST",
    f"/orgs/{oid}/grading/attempts/{aid}",
    {"score": 85, "feedback": "Good explanation!"},
    headers=AUTH,
)
check("manual grade", r.get("data", {}).get("score") == 85)

# Progress
r = api("GET", f"/orgs/{oid}/progress/me", headers=AUTH)
check("overall progress", r.get("data", {}).get("skills_total", 0) >= 1)

r = api("GET", f"/orgs/{oid}/progress/me/skills/{sid}", headers=AUTH)
check("skill progress", r.get("data") is not None)

# ════════════════════════════════════════════════════════
section("7. Projects + Submissions + Reviews")
r = api(
    "POST",
    f"/orgs/{oid}/projects",
    {
        "title": "AI Chatbot",
        "description": "Build one",
        "instructions": "## Task\nBuild a chatbot using the OpenAI API.",
        "rubric": [
            {"criterion": "Functionality", "max_score": 40},
            {"criterion": "Code Quality", "max_score": 30},
            {"criterion": "Innovation", "max_score": 30},
        ],
        "max_score": 100,
        "late_penalty_pct": 20,
    },
    headers=AUTH,
    expect=201,
)
check("create project", r.get("data", {}).get("title") == "AI Chatbot")
pid = r.get("data", {}).get("id", "")

r = api("GET", f"/orgs/{oid}/projects", headers=AUTH)
check("list projects", r.get("meta", {}).get("total") >= 1)

r = api("GET", f"/orgs/{oid}/projects/{pid}", headers=AUTH)
check("project detail has rubric", len(r.get("data", {}).get("rubric", [])) == 3)

# Deliverable
r = api(
    "POST",
    f"/orgs/{oid}/projects/{pid}/deliverables",
    {
        "name": "Source Code",
        "type": "text",
        "required": False,
    },
    headers=AUTH,
    expect=201,
)
check("create deliverable", r.get("data", {}).get("name") == "Source Code")

# Submission lifecycle
r = api("POST", f"/orgs/{oid}/projects/{pid}/submissions", headers=AUTH, expect=201)
check("create submission v1", r.get("data", {}).get("version") == 1)
subid = r.get("data", {}).get("id", "")

r = api("POST", f"/orgs/{oid}/projects/{pid}/submissions/{subid}/submit", headers=AUTH)
check("submit draft", r.get("data", {}).get("status") == "submitted")
check("not late", r.get("data", {}).get("is_late") is False)

# Review: approve
r = api(
    "POST",
    f"/orgs/{oid}/submissions/{subid}/reviews",
    {
        "status": "approved",
        "score": 92,
        "feedback": "Excellent chatbot!",
        "score_breakdown": {"Functionality": 38, "Code Quality": 28, "Innovation": 26},
    },
    headers=AUTH,
    expect=201,
)
check("review approved", r.get("data", {}).get("status") == "approved")
check("review score=92", r.get("data", {}).get("score") == 92)

# Check final score
r = api("GET", f"/orgs/{oid}/projects/{pid}/submissions/{subid}", headers=AUTH)
check("final_score=92", r.get("data", {}).get("final_score") == 92)
check("status=approved", r.get("data", {}).get("status") == "approved")

# Review list
r = api("GET", f"/orgs/{oid}/submissions/{subid}/reviews", headers=AUTH)
check("review list", len(r.get("data", [])) >= 1)

# Pending reviews
r = api("GET", f"/orgs/{oid}/reviews/pending", headers=AUTH)
check("pending reviews endpoint", isinstance(r.get("data"), list))

# Second submission
r = api("POST", f"/orgs/{oid}/projects/{pid}/submissions", headers=AUTH, expect=201)
check("create submission v2", r.get("data", {}).get("version") == 2)

# ════════════════════════════════════════════════════════
section("8. AI Evaluation Settings")
r = api("GET", f"/orgs/{oid}/settings/evaluation", headers=AUTH)
check("eval settings default", r.get("data", {}).get("enabled") is False)

r = api(
    "PUT",
    f"/orgs/{oid}/settings/evaluation",
    {
        "enabled": True,
        "monthly_budget_usd": 50,
        "auto_evaluate": False,
    },
    headers=AUTH,
)
check("update eval settings", r.get("data", {}).get("enabled") is True)

r = api("GET", f"/orgs/{oid}/evaluation/usage", headers=AUTH)
check("eval usage", r.get("data", {}).get("total_tasks") == 0)

r = api("GET", f"/orgs/{oid}/evaluation/tasks", headers=AUTH)
check("eval tasks list", isinstance(r.get("data"), list))

# ════════════════════════════════════════════════════════
section("9. Portfolio")
r = api("GET", "/portfolio/profile", headers=AUTH)
check("get profile", r.get("data", {}).get("username") is not None)
username = r.get("data", {}).get("username", "")

r = api(
    "PUT",
    "/portfolio/profile",
    {
        "headline": "AI Builder",
        "bio": "Building the future",
        "location": "Beijing",
        "website_url": "https://example.com",
        "social_links": {"github": "https://github.com/smoke"},
    },
    headers=AUTH,
)
check("update profile", r.get("data", {}).get("headline") == "AI Builder")

r = api(
    "POST",
    "/portfolio/items",
    {
        "title": "My Chatbot Project",
        "description": "Built with OpenAI",
        "tags": ["ai", "chatbot"],
        "visibility": "public",
        "featured": True,
    },
    headers=AUTH,
    expect=201,
)
check("create portfolio item", r.get("data", {}).get("title") == "My Chatbot Project")
iid = r.get("data", {}).get("id", "")

r = api("GET", "/portfolio/items", headers=AUTH)
check("list items", len(r.get("data", [])) >= 1)

r = api("PUT", f"/portfolio/items/{iid}", {"title": "Chatbot v2"}, headers=AUTH)
check("update item", r.get("data", {}).get("title") == "Chatbot v2")

r = api("GET", "/portfolio/badges", headers=AUTH)
check("badges list", isinstance(r.get("data"), list))

# ════════════════════════════════════════════════════════
section("10. Public Profile")
r = api("GET", f"/u/{username}")
check("public profile", r.get("data", {}).get("display_name") == "Smoke Updated")
check("public skills", isinstance(r.get("data", {}).get("skills", []), list))
check("public featured", isinstance(r.get("data", {}).get("featured_items", []), list))
check("no email exposed", r.get("data", {}).get("email") is None)

r = api("GET", f"/u/{username}/items")
check("public items list", isinstance(r.get("data"), list))

# ════════════════════════════════════════════════════════
section("11. Error Handling")
r = api("GET", "/auth/me", expect=401)
check("401 on no auth", True)

r = api(
    "POST", "/auth/register", {"email": "bad", "password": "x", "display_name": "X"}, expect=422
)
check("422 on validation", True)

r = api("GET", f"/orgs/{oid}/skills/nonexistent", headers=AUTH, expect=404)
check("404 on not found", True)

r = api(
    "POST",
    "/auth/register",
    {"email": email, "password": "Smoke123!", "display_name": "Dup"},
    expect=409,
)
check("409 on duplicate", True)

# ════════════════════════════════════════════════════════
print(f"\n{'=' * 60}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed")
print(f"{'=' * 60}")
sys.exit(1 if FAIL > 0 else 0)
