import { beforeEach, describe, expect, it, vi } from "vitest";

// server-only guard + next/headers are server-runtime shims
vi.mock("server-only", () => ({}));
vi.mock("next/headers", () => ({ headers: vi.fn() }));

import { themeTokensToCss } from "@/lib/site-context";

describe("themeTokensToCss (R366 — the white-label style-tag generator)", () => {
  it("converts exact hex colors to HSL triples", () => {
    const css = themeTokensToCss({ primary: "#ff0000" });
    expect(css).toBe(":root { --primary: 0 100% 50%; }");
    expect(themeTokensToCss({ accent: "#00ff00" })).toContain("--accent: 120 100% 50%;");
    expect(themeTokensToCss({ background: "#0000ff" })).toContain("--background: 240 100% 50%;");
    // greys: zero saturation, correct lightness
    expect(themeTokensToCss({ muted: "#808080" })).toContain("--muted: 0 0% 50.2%;");
    expect(themeTokensToCss({ foreground: "#000000" })).toContain("--foreground: 0 0% 0%;");
    expect(themeTokensToCss({ border: "#ffffff" })).toContain("--border: 0 0% 100%;");
    // R527 mutation kills: a LIGHT saturated color exercises the l>0.5
    // saturation denominator (2-max-min) — the flat d/(max+min) mutant
    // reports 33.2% instead of 100%...
    expect(themeTokensToCss({ primary: "#ff8080" })).toContain("--primary: 0 100% 75.1%;");
    // ...and a red-max, blue>green color exercises the hue wrap (+6):
    // without it the hue goes negative instead of 330.
    expect(themeTokensToCss({ primary: "#ff0080" })).toContain("--primary: 330 100% 50%;");
  });

  it("NEVER emits garbage into the style tag (injection guard)", () => {
    for (const bad of [
      "red",
      "#fff", // 3-digit not allowed
      "#gggggg",
      "#12345", // 5 digits
      "#1234567", // 7 digits
      "url(javascript:alert(1))",
      "#ff0000; } body { display:none",
    ]) {
      expect(themeTokensToCss({ primary: bad })).toBe("");
    }
    // R527: the ^…$ anchors are load-bearing — an EMBEDDED valid hex
    // ("x#ff0000; }") must not satisfy the pattern
    for (const bad of ["x#ff0000", "#ff0000; } body { display:none", " #ff0000"]) {
      expect(themeTokensToCss({ primary: bad })).toBe("");
    }
  });

  it("maps the radius enum and rejects out-of-set values", () => {
    expect(themeTokensToCss({ radius: "none" })).toBe(":root { --radius: 0rem; }");
    expect(themeTokensToCss({ radius: "sm" })).toContain("0.25rem");
    expect(themeTokensToCss({ radius: "md" })).toContain("0.5rem");
    expect(themeTokensToCss({ radius: "lg" })).toContain("0.75rem");
    expect(themeTokensToCss({ radius: "full" })).toContain("9999px");
    expect(themeTokensToCss({ radius: "2rem" })).toBe("");
    expect(themeTokensToCss({ radius: "calc(1px)" })).toBe("");
  });

  it("ignores unknown token keys and returns '' for empty input", () => {
    expect(themeTokensToCss({})).toBe("");
    expect(themeTokensToCss({ evil: "#ff0000" } as Record<string, string>)).toBe("");
  });

  it("combines multiple valid tokens in stable key order", () => {
    const css = themeTokensToCss({
      radius: "md",
      primary: "#336699",
      accent: "#c0ffee",
    });
    expect(css.indexOf("--primary")).toBeLessThan(css.indexOf("--accent"));
    expect(css.indexOf("--accent")).toBeLessThan(css.indexOf("--radius"));
    expect(css.startsWith(":root {")).toBe(true);
    expect(css.endsWith("}")).toBe(true);
  });
});

describe("portalApi (R366 — the portal network layer)", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.restoreAllMocks();
  });

  it("prefers the guest JWT over the product access token", async () => {
    sessionStorage.setItem("client_portal_jwt", "guest-jwt");
    const { useAuthStore } = await import("@/stores/auth");
    useAuthStore.setState({ accessToken: "member-token" });
    const spy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify({ data: 1 }), { status: 200 }));
    const { portalApi } = await import("@/lib/client-portal");
    await portalApi("/x");
    const headers = (spy.mock.calls[0]![1] as RequestInit).headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer guest-jwt");
  });

  it("falls back to the member token when no guest JWT exists", async () => {
    const { useAuthStore } = await import("@/stores/auth");
    useAuthStore.setState({ accessToken: "member-token" });
    const spy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify({ data: 1 }), { status: 200 }));
    const { portalApi } = await import("@/lib/client-portal");
    await portalApi("/x");
    const headers = (spy.mock.calls[0]![1] as RequestInit).headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer member-token");
  });

  it("maps timeout, network failure and error bodies to ApiError codes", async () => {
    const { portalApi } = await import("@/lib/client-portal");
    const { ApiError } = await import("@/lib/api");

    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new DOMException("t", "TimeoutError"));
    await expect(portalApi("/x")).rejects.toMatchObject({ code: "TIMEOUT", status: 0 });

    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new TypeError("net"));
    await expect(portalApi("/x")).rejects.toMatchObject({ code: "NETWORK_ERROR" });

    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ error: { code: "CLIENT_ACCESS_DENIED", message: "no" } }), {
        status: 401,
      }),
    );
    await expect(portalApi("/x")).rejects.toMatchObject({
      code: "CLIENT_ACCESS_DENIED",
      status: 401,
    });

    // non-JSON error body → UNKNOWN, never a crash
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(new Response("<html>", { status: 503 }));
    const err = (await portalApi("/x").catch((e: unknown) => e)) as InstanceType<typeof ApiError>;
    expect(err).toBeInstanceOf(ApiError);
    expect(err.code).toBe("UNKNOWN");
  });

  it("returns undefined for 204 responses", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(new Response(null, { status: 204 }));
    const { portalApi } = await import("@/lib/client-portal");
    await expect(portalApi("/x")).resolves.toBeUndefined();
  });
});
