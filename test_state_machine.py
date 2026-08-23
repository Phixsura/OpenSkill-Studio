#!/usr/bin/env python3
"""State machine invariant tests for the Skill Pack Registry API."""

import json
import time
import random
import string
import requests

BASE = "http://localhost:8000/api/v1"


def rand_str(n=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def rand_email():
    return f"test_{rand_str(12)}@example.com"


# ── Results tracking ─────────────────────────────────────────


results = []


def record(name, passed, detail=""):
    emoji = "✅" if passed else "❌"
    results.append((name, passed, detail))
    print(f"  {emoji} {name}" + (f"  ({detail})" if detail else ""))


# ── Helpers ──────────────────────────────────────────────────


def register_user():
    email = rand_email()
    password = "TestPassword123!"
    for attempt in range(10):
        r = requests.post(f"{BASE}/auth/register", json={
            "email": email,
            "password": password,
            "display_name": f"Tester {rand_str(4)}",
        })
        if r.status_code == 429:
            wait = 20 * (attempt + 1)
            print(f"    Rate limited on register, waiting {wait}s (attempt {attempt+1}/10)...")
            time.sleep(wait)
            continue
        break
    assert r.status_code == 201, f"Register failed: {r.status_code} {r.text}"
    data = r.json()
    token = data["access_token"]
    user_id = data["user"]["id"]
    return token, user_id, email


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_org(token):
    slug = f"test-org-{rand_str(8)}"
    r = requests.post(f"{BASE}/orgs", json={
        "name": f"Test Org {rand_str(4)}",
        "slug": slug,
        "description": "Test org for state machine tests",
    }, headers=auth_headers(token))
    assert r.status_code == 201, f"Create org failed: {r.status_code} {r.text}"
    return r.json()["data"]["id"]


def create_category(token, org_id):
    slug = f"cat-{rand_str(8)}"
    r = requests.post(f"{BASE}/orgs/{org_id}/categories", json={
        "name": f"Category {rand_str(4)}",
        "slug": slug,
    }, headers=auth_headers(token))
    assert r.status_code == 201, f"Create category failed: {r.status_code} {r.text}"
    return r.json()["data"]["id"]


def create_skill(token, org_id, category_id, name=None):
    name = name or f"Skill {rand_str(6)}"
    slug = f"skill-{rand_str(8)}"
    r = requests.post(f"{BASE}/orgs/{org_id}/skills", json={
        "name": name,
        "slug": slug,
        "category_id": category_id,
        "description": "A test skill",
        "learning_content": "# Test\nSome content",
        "difficulty": "beginner",
        "estimated_minutes": 30,
        "tags": ["test"],
    }, headers=auth_headers(token))
    assert r.status_code == 201, f"Create skill failed: {r.status_code} {r.text}"
    return r.json()["data"]["id"]


def create_template(token, org_id, name=None):
    name = name or f"Template {rand_str(6)}"
    r = requests.post(f"{BASE}/orgs/{org_id}/project-templates", json={
        "name": name,
        "description": "A test project template",
        "instructions": "Build something cool",
        "project_type": "general",
        "difficulty": "intermediate",
        "suggested_minutes": 60,
        "max_score": 100,
        "rubric": [{"criterion": "Quality", "max_score": 100, "description": "Overall quality"}],
        "deliverables": [],
    }, headers=auth_headers(token))
    assert r.status_code == 201, f"Create template failed: {r.status_code} {r.text}"
    return r.json()["data"]["id"]


def create_pack(token, org_id, name=None, visibility="public"):
    name = name or f"Pack {rand_str(6)}"
    r = requests.post(f"{BASE}/orgs/{org_id}/packs", json={
        "name": name,
        "description": "A test skill pack",
        "summary": "Test pack summary",
        "visibility": visibility,
        "difficulty": "beginner",
    }, headers=auth_headers(token))
    assert r.status_code == 201, f"Create pack failed: {r.status_code} {r.text}"
    return r.json()["data"]["id"]


def add_skill_to_pack(token, org_id, pack_id, skill_id, sort_order=0):
    r = requests.post(f"{BASE}/orgs/{org_id}/packs/{pack_id}/skills", json={
        "skill_id": skill_id,
        "sort_order": sort_order,
    }, headers=auth_headers(token))
    return r


def add_template_to_pack(token, org_id, pack_id, template_id, sort_order=0):
    r = requests.post(f"{BASE}/orgs/{org_id}/packs/{pack_id}/templates", json={
        "template_id": template_id,
        "sort_order": sort_order,
    }, headers=auth_headers(token))
    return r


def publish_release(token, org_id, pack_id, version, changelog=None):
    r = requests.post(f"{BASE}/orgs/{org_id}/packs/{pack_id}/releases", json={
        "version": version,
        "changelog": changelog or f"Release {version}",
    }, headers=auth_headers(token))
    return r


def install_pack(token, org_id, pack_id, version=None):
    body = {"pack_id": pack_id}
    if version:
        body["version"] = version
    r = requests.post(f"{BASE}/orgs/{org_id}/installations", json=body,
                      headers=auth_headers(token))
    return r


def delete_pack(token, org_id, pack_id):
    return requests.delete(f"{BASE}/orgs/{org_id}/packs/{pack_id}",
                           headers=auth_headers(token))


def update_pack(token, org_id, pack_id, **fields):
    return requests.put(f"{BASE}/orgs/{org_id}/packs/{pack_id}",
                        json=fields, headers=auth_headers(token))


def get_pack(token, org_id, pack_id):
    return requests.get(f"{BASE}/orgs/{org_id}/packs/{pack_id}",
                        headers=auth_headers(token))


def get_installation(token, org_id, install_id):
    return requests.get(f"{BASE}/orgs/{org_id}/installations/{install_id}",
                        headers=auth_headers(token))


def delete_installation(token, org_id, install_id):
    return requests.delete(f"{BASE}/orgs/{org_id}/installations/{install_id}",
                           headers=auth_headers(token))


def fork_installation(token, org_id, install_id):
    return requests.post(f"{BASE}/orgs/{org_id}/installations/{install_id}/fork",
                         headers=auth_headers(token))


def diff_installation(token, org_id, install_id, version):
    return requests.get(f"{BASE}/orgs/{org_id}/installations/{install_id}/diff",
                        params={"version": version}, headers=auth_headers(token))


def get_release(token, org_id, pack_id, version):
    return requests.get(f"{BASE}/orgs/{org_id}/packs/{pack_id}/releases/{version}",
                        headers=auth_headers(token))


def update_skill(token, org_id, skill_id, **fields):
    return requests.put(f"{BASE}/orgs/{org_id}/skills/{skill_id}",
                        json=fields, headers=auth_headers(token))


# ── Setup ────────────────────────────────────────────────────


print("=" * 60)
print("SKILL PACK REGISTRY — STATE MACHINE INVARIANT TESTS")
print("=" * 60)
print()

print("Setting up test user and org...")
token, user_id, email = register_user()
print(f"  Registered user: {email}")
time.sleep(2)
org_id = create_org(token)
print(f"  Created org: {org_id}")
cat_id = create_category(token, org_id)
print(f"  Created category: {cat_id}")
print()


# ═══════════════════════════════════════════════════════════
# PACK STATE TESTS
# ═══════════════════════════════════════════════════════════

print("-" * 60)
print("PACK STATE TESTS")
print("-" * 60)

# ── Test 1: Create pack (draft) -> DELETE -> attempt PUT update -> expect 404
print("\nTest group: Deleted pack operations")
pack_id = create_pack(token, org_id)
r = delete_pack(token, org_id, pack_id)
assert r.status_code == 204, f"Delete pack failed: {r.status_code}"

r = update_pack(token, org_id, pack_id, name="Updated Name")
record("Deleted pack -> PUT update -> 404", r.status_code == 404,
       f"got {r.status_code}")

# ── Test 2: Create pack (draft) -> DELETE -> attempt POST add_skill -> expect 404
skill_id_for_test = create_skill(token, org_id, cat_id)
pack_id = create_pack(token, org_id)
r = delete_pack(token, org_id, pack_id)
assert r.status_code == 204

r = add_skill_to_pack(token, org_id, pack_id, skill_id_for_test)
record("Deleted pack -> POST add_skill -> 404", r.status_code == 404,
       f"got {r.status_code}")

# ── Test 3: Create pack (draft) -> DELETE -> attempt POST release -> expect 404
pack_id = create_pack(token, org_id)
# Add a skill first so we could theoretically release
sk = create_skill(token, org_id, cat_id)
add_skill_to_pack(token, org_id, pack_id, sk)
r = delete_pack(token, org_id, pack_id)
assert r.status_code == 204

r = publish_release(token, org_id, pack_id, "1.0.0")
record("Deleted pack -> POST release -> 404", r.status_code == 404,
       f"got {r.status_code}")

# ── Test 4: Create pack -> publish release -> verify status=published -> DELETE -> verify can't access
print("\nTest group: Published pack lifecycle")
pack_id = create_pack(token, org_id)
sk = create_skill(token, org_id, cat_id)
add_skill_to_pack(token, org_id, pack_id, sk)
r = publish_release(token, org_id, pack_id, "1.0.0")
assert r.status_code == 201, f"Publish failed: {r.status_code} {r.text}"

r = get_pack(token, org_id, pack_id)
assert r.status_code == 200
status = r.json()["data"]["status"]
record("Pack status after publish is 'published'", status == "published",
       f"got '{status}'")

r = delete_pack(token, org_id, pack_id)
assert r.status_code == 204

r = get_pack(token, org_id, pack_id)
record("Published pack -> DELETE -> GET -> 404", r.status_code == 404,
       f"got {r.status_code}")


# ═══════════════════════════════════════════════════════════
# INSTALL STATE TESTS
# ═══════════════════════════════════════════════════════════

print()
print("-" * 60)
print("INSTALL STATE TESTS")
print("-" * 60)

# We need a second org to install into (since the publishing org is org_id)
token2, user2_id, email2 = register_user()
time.sleep(2)
org2_id = create_org(token2)
cat2_id = create_category(token2, org2_id)
print(f"\n  Created consumer org: {org2_id} (user: {email2})")

# Create a publishable pack in org_id
pack_id = create_pack(token, org_id)
sk = create_skill(token, org_id, cat_id)
add_skill_to_pack(token, org_id, pack_id, sk)
r = publish_release(token, org_id, pack_id, "1.0.0")
assert r.status_code == 201, f"Publish failed: {r.status_code} {r.text}"
print(f"  Published pack: {pack_id}")

# ── Test 5: Install pack -> DELETE (remove) -> reinstall -> expect 201
print("\nTest group: Install/remove/reinstall cycle")
r = install_pack(token2, org2_id, pack_id)
assert r.status_code == 201, f"Install failed: {r.status_code} {r.text}"
install_id = r.json()["data"]["id"]

r = delete_installation(token2, org2_id, install_id)
assert r.status_code == 204, f"Remove install failed: {r.status_code}"

r = install_pack(token2, org2_id, pack_id)
record("Install -> remove -> reinstall -> 201", r.status_code == 201,
       f"got {r.status_code}")
install_id_new = r.json()["data"]["id"]
# Clean up for next tests
r = delete_installation(token2, org2_id, install_id_new)
assert r.status_code == 204

# ── Test 6: Install pack -> fork -> attempt fork again -> expect 422
print("\nTest group: Fork invariants")
r = install_pack(token2, org2_id, pack_id)
assert r.status_code == 201
install_id = r.json()["data"]["id"]

r = fork_installation(token2, org2_id, install_id)
assert r.status_code == 200, f"Fork failed: {r.status_code} {r.text}"

r = fork_installation(token2, org2_id, install_id)
record("Install -> fork -> fork again -> 422", r.status_code == 422,
       f"got {r.status_code}")

# ── Test 7: Install -> fork -> attempt diff -> expect 422 (forked, no updates)
r = diff_installation(token2, org2_id, install_id, "1.0.0")
# A forked installation may return 422 directly or may return data with
# update_available=False and reason=forked.  The check_update logic in
# get_installation already handles the "forked" case by returning
# update_available=False.  The diff endpoint itself may or may not block
# the call.  Let's check what actually happens and record it.
# Looking at the code: compute_diff doesn't check fork status, it just
# compares manifests.  But the spec says forked installs shouldn't diff.
# Let's see what the API returns.
if r.status_code == 422:
    record("Forked install -> diff -> 422", True, "correctly rejected")
elif r.status_code == 200:
    # The API allows diff on forked installs (returns the diff anyway).
    # This is arguably a design choice — the diff can still be useful for
    # information even if the install is forked. We'll record the actual
    # behavior.
    record("Forked install -> diff -> 422", False,
           f"got 200 (API allows diff on forked installs)")
else:
    record("Forked install -> diff -> 422", False, f"got {r.status_code}")

# Clean up forked install
r = delete_installation(token2, org2_id, install_id)
assert r.status_code == 204

# ── Test 8: Install -> DELETE -> attempt GET -> expect 404
print("\nTest group: Removed install operations")
r = install_pack(token2, org2_id, pack_id)
assert r.status_code == 201
install_id = r.json()["data"]["id"]

r = delete_installation(token2, org2_id, install_id)
assert r.status_code == 204

r = get_installation(token2, org2_id, install_id)
record("Install -> DELETE -> GET -> 404", r.status_code == 404,
       f"got {r.status_code}")

# ── Test 9: Install -> DELETE -> attempt fork -> expect 404
r = fork_installation(token2, org2_id, install_id)
record("Install -> DELETE -> fork -> 404", r.status_code == 404,
       f"got {r.status_code}")


# ═══════════════════════════════════════════════════════════
# RELEASE IMMUTABILITY TESTS
# ═══════════════════════════════════════════════════════════

print()
print("-" * 60)
print("RELEASE IMMUTABILITY TESTS")
print("-" * 60)

# Create a pack with a skill, publish v1.0.0, modify source skill,
# publish v1.0.1, verify v1.0.0 manifest is unchanged
print("\nTest group: Release manifest immutability")
pack_id = create_pack(token, org_id)
sk_immut = create_skill(token, org_id, cat_id, name="Immutability Test Skill")
add_skill_to_pack(token, org_id, pack_id, sk_immut)

# Publish v1.0.0
r = publish_release(token, org_id, pack_id, "1.0.0")
assert r.status_code == 201, f"Publish v1.0.0 failed: {r.status_code} {r.text}"

# Get v1.0.0 manifest before modification
r = get_release(token, org_id, pack_id, "1.0.0")
assert r.status_code == 200
manifest_before = r.json()["data"]["manifest"]

# Modify the source skill
r = update_skill(token, org_id, sk_immut, name="Modified Skill Name",
                 description="Modified description for immutability test")
assert r.status_code == 200, f"Update skill failed: {r.status_code} {r.text}"

# Publish v1.0.1 (should capture modified skill)
r = publish_release(token, org_id, pack_id, "1.0.1")
assert r.status_code == 201, f"Publish v1.0.1 failed: {r.status_code} {r.text}"

# Get v1.0.0 manifest after modification and new release
r = get_release(token, org_id, pack_id, "1.0.0")
assert r.status_code == 200
manifest_after = r.json()["data"]["manifest"]

record("v1.0.0 manifest unchanged after skill modification + v1.0.1 publish",
       manifest_before == manifest_after,
       "manifests differ!" if manifest_before != manifest_after else "identical")

# Also verify that v1.0.1 actually captured the modification
r = get_release(token, org_id, pack_id, "1.0.1")
assert r.status_code == 200
manifest_v101 = r.json()["data"]["manifest"]
v101_skills = manifest_v101.get("skills", [])
if v101_skills:
    v101_skill_name = v101_skills[0].get("name", "")
    record("v1.0.1 captured modified skill name",
           v101_skill_name == "Modified Skill Name",
           f"got '{v101_skill_name}'")
else:
    record("v1.0.1 captured modified skill name", False, "no skills in manifest")


# ═══════════════════════════════════════════════════════════
# DUPLICATE PROTECTION TESTS
# ═══════════════════════════════════════════════════════════

print()
print("-" * 60)
print("DUPLICATE PROTECTION TESTS")
print("-" * 60)

# ── Test: Install same pack twice -> expect 409
print("\nTest group: Duplicate install")
# Create and publish a fresh pack
pack_dup = create_pack(token, org_id)
sk_dup = create_skill(token, org_id, cat_id)
add_skill_to_pack(token, org_id, pack_dup, sk_dup)
r = publish_release(token, org_id, pack_dup, "1.0.0")
assert r.status_code == 201

# Need a fresh consumer org (no prior installs)
token3, user3_id, email3 = register_user()
time.sleep(2)
org3_id = create_org(token3)

r = install_pack(token3, org3_id, pack_dup)
assert r.status_code == 201, f"First install failed: {r.status_code} {r.text}"

r = install_pack(token3, org3_id, pack_dup)
record("Install same pack twice -> 409", r.status_code == 409,
       f"got {r.status_code}")

# ── Test: Publish same version twice -> expect 409
print("\nTest group: Duplicate version")
pack_ver = create_pack(token, org_id)
sk_ver = create_skill(token, org_id, cat_id)
add_skill_to_pack(token, org_id, pack_ver, sk_ver)

r = publish_release(token, org_id, pack_ver, "1.0.0")
assert r.status_code == 201

r = publish_release(token, org_id, pack_ver, "1.0.0")
record("Publish same version twice -> 409", r.status_code == 409,
       f"got {r.status_code}")

# ── Test: Add same skill to pack twice -> expect 409
print("\nTest group: Duplicate pack contents")
pack_content = create_pack(token, org_id)
sk_content = create_skill(token, org_id, cat_id)

r = add_skill_to_pack(token, org_id, pack_content, sk_content)
assert r.status_code == 201

r = add_skill_to_pack(token, org_id, pack_content, sk_content)
record("Add same skill to pack twice -> 409", r.status_code == 409,
       f"got {r.status_code}")

# ── Test: Add same template to pack twice -> expect 409
tmpl_id = create_template(token, org_id)

r = add_template_to_pack(token, org_id, pack_content, tmpl_id)
assert r.status_code == 201

r = add_template_to_pack(token, org_id, pack_content, tmpl_id)
record("Add same template to pack twice -> 409", r.status_code == 409,
       f"got {r.status_code}")


# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

passed = sum(1 for _, p, _ in results if p)
failed = sum(1 for _, p, _ in results if not p)
total = len(results)

print(f"\nTotal:  {total}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print()

if failed > 0:
    print("FAILURES:")
    for name, p, detail in results:
        if not p:
            print(f"  ❌ {name}: {detail}")
    print()

if failed == 0:
    print("All tests passed!")
else:
    print(f"{failed}/{total} tests failed.")
