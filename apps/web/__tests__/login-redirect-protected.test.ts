// R304: redirectToLoginIfProtected (private; exercised via sharedRefresh's
// failure path). R101[M15]: /platform and /partner live OUTSIDE the
// /dashboard URL prefix, so session expiry there must still bounce to login;
// public pages must NOT be redirected. A wrong protected-set either strands
// a user on a blank protected pane or yanks them off a public page.
import { beforeEach, describe, expect, it, vi } from "vitest";

import { sharedRefresh } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const USER = {
  id: "u1",
  email: "a@b.c",
  email_verified: true,
  display_name: "A",
  avatar_url: null,
  role: "student",
  created_at: "2026-01-01T00:00:00Z",
};

function setPath(pathname: string) {
  Object.defineProperty(window, "location", {
    value: { pathname, href: "", assign: vi.fn() },
    writable: true,
  });
}

beforeEach(() => {
  useAuthStore.getState().clearAuth();
  vi.restoreAllMocks();
  // a failed refresh triggers redirectToLoginIfProtected
  vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("", { status: 401 }));
});

describe("redirectToLoginIfProtected via sharedRefresh (R304)", () => {
  for (const path of ["/dashboard/x", "/platform/tenants", "/partner/statements"]) {
    it(`bounces to login from protected path ${path}`, async () => {
      setPath(path);
      await expect(sharedRefresh()).rejects.toBeTruthy();
      expect(window.location.href).toBe(`/login?redirect=${encodeURIComponent(path)}`);
    });
  }

  for (const path of ["/", "/login", "/register", "/pricing", "/verify/abc"]) {
    it(`does NOT redirect from public path ${path}`, async () => {
      setPath(path);
      await expect(sharedRefresh()).rejects.toBeTruthy();
      expect(window.location.href).toBe(""); // untouched
    });
  }
});
