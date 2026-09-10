// R302: apiWithAuth's own refresh/retry/impersonation logic. Everywhere else
// this function is mocked; here we exercise it directly — the R101[H11]
// impersonation guard is security-critical (an expired impersonation 401 must
// NOT auto-refresh into the support operator's own privileged token).
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiWithAuth } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

// base64url JWT with the given payload (client never verifies the signature)
function jwt(payload: Record<string, unknown>): string {
  const b64 = (o: unknown) =>
    btoa(JSON.stringify(o)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  return `${b64({ alg: "HS256" })}.${b64(payload)}.sig`;
}

const USER = {
  id: "u1",
  email: "a@b.c",
  email_verified: true,
  display_name: "A",
  avatar_url: null,
  role: "student",
  created_at: "2026-01-01T00:00:00Z",
};

beforeEach(() => {
  useAuthStore.getState().clearAuth();
  vi.restoreAllMocks();
  // jsdom has no navigation; stub location so redirectToLoginIfProtected is safe
  Object.defineProperty(window, "location", {
    value: { pathname: "/dashboard", href: "", assign: vi.fn() },
    writable: true,
  });
});

afterEach(() => {
  useAuthStore.getState().clearAuth();
});

describe("apiWithAuth (R302)", () => {
  it("R101[H11]: an expired impersonation token 401 ends the session, never refreshes", async () => {
    useAuthStore.getState().setAuth(jwt({ sub: "target", imp: "operator" }), USER);
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response("", { status: 401 }));

    await expect(apiWithAuth("/tenants/mine")).rejects.toMatchObject({
      code: "IMPERSONATION_EXPIRED",
    });
    // exactly ONE call — no refresh attempt, no retry
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    // session cleared (operator's privileges never reinstated)
    expect(useAuthStore.getState().accessToken).toBeNull();
  });

  it("returns undefined on 204 without parsing a body", async () => {
    useAuthStore.getState().setAuth(jwt({ sub: "u1" }), USER);
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(new Response(null, { status: 204 }));
    await expect(apiWithAuth("/x", { method: "DELETE" })).resolves.toBeUndefined();
  });

  it("surfaces the backend error code on a non-401 failure", async () => {
    useAuthStore.getState().setAuth(jwt({ sub: "u1" }), USER);
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ error: { code: "TENANT_FORBIDDEN", message: "no" } }), {
        status: 403,
      }),
    );
    try {
      await apiWithAuth("/x");
      throw new Error("expected ApiError");
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).code).toBe("TENANT_FORBIDDEN");
      expect((e as ApiError).status).toBe(403);
    }
  });
});
