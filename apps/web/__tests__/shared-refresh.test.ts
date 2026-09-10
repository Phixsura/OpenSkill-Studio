// R303: sharedRefresh's concurrency dedup + refreshAccessToken's validation.
// Refresh tokens ROTATE on use, so two concurrent RAW refreshes race — the
// loser presents a just-revoked token, 401s, and wrongly clears the session.
// sharedRefresh must collapse N concurrent callers into ONE /auth/refresh.
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError, sharedRefresh } from "@/lib/api";
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

beforeEach(() => {
  useAuthStore.getState().clearAuth();
  vi.restoreAllMocks();
  Object.defineProperty(window, "location", {
    value: { pathname: "/dashboard", href: "", assign: vi.fn() },
    writable: true,
  });
});

describe("sharedRefresh (R303)", () => {
  it("collapses concurrent callers into a SINGLE /auth/refresh (rotation-safe)", async () => {
    let calls = 0;
    vi.spyOn(globalThis, "fetch").mockImplementation(async () => {
      calls += 1;
      // small delay so the second caller arrives while the first is in flight
      await new Promise((r) => setTimeout(r, 10));
      return new Response(JSON.stringify({ access_token: "fresh-tok", user: USER }), {
        status: 200,
      });
    });

    const [a, b, c] = await Promise.all([sharedRefresh(), sharedRefresh(), sharedRefresh()]);
    expect(calls).toBe(1); // ONE network refresh for three concurrent callers
    expect(a).toBe("fresh-tok");
    expect(b).toBe("fresh-tok");
    expect(c).toBe("fresh-tok");
    expect(useAuthStore.getState().accessToken).toBe("fresh-tok");
  });

  it("allows a NEW refresh after the previous one settles (promise not stuck)", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(
      async () => new Response(JSON.stringify({ access_token: "t2", user: USER }), { status: 200 }),
    );
    await sharedRefresh();
    const second = await sharedRefresh(); // must actually run again, not a stale cached promise
    expect(second).toBe("t2");
  });

  it("clears auth + throws SESSION_EXPIRED on a non-ok refresh", async () => {
    useAuthStore.getState().setAuth("old", USER);
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(new Response("", { status: 401 }));
    await expect(sharedRefresh()).rejects.toMatchObject({ code: "SESSION_EXPIRED" });
    expect(useAuthStore.getState().accessToken).toBeNull();
  });

  it("rejects a 200 refresh whose body is missing the token (INVALID_REFRESH)", async () => {
    useAuthStore.getState().setAuth("old", USER);
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ user: USER }), { status: 200 }), // no access_token
    );
    await expect(sharedRefresh()).rejects.toMatchObject({ code: "INVALID_REFRESH" });
    expect(useAuthStore.getState().accessToken).toBeNull();
  });

  it("maps a network failure during refresh to NETWORK_ERROR + clears auth", async () => {
    useAuthStore.getState().setAuth("old", USER);
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new TypeError("down"));
    await expect(sharedRefresh()).rejects.toBeInstanceOf(ApiError);
    expect(useAuthStore.getState().accessToken).toBeNull();
  });
});
