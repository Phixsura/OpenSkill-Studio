import { describe, it, expect, vi } from "vitest";
import { api, ApiError } from "@/lib/api";

describe("api client", () => {
  it("should return parsed JSON on success", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ status: "ok" }), { status: 200 }),
    );

    const data = await api<{ status: string }>("/health");
    expect(data.status).toBe("ok");
  });

  it("should throw ApiError on non-ok response", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          error: { code: "NOT_FOUND", message: "Not found" },
        }),
        { status: 404 },
      ),
    );

    await expect(api("/missing")).rejects.toThrow(ApiError);
  });

  // ── R301: error-extraction defensive arcs ──

  it("maps a non-JSON success body to PARSE_ERROR (client R87 class)", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response("<html>not json</html>", { status: 200 }),
    );
    try {
      await api("/health");
      throw new Error("expected ApiError");
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).code).toBe("PARSE_ERROR");
    }
  });

  it("falls back to UNKNOWN when the error body has no error.code", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "something else" }), { status: 500 }),
    );
    try {
      await api("/x");
      throw new Error("expected ApiError");
    } catch (e) {
      expect((e as ApiError).code).toBe("UNKNOWN");
      expect((e as ApiError).status).toBe(500);
      expect((e as ApiError).message).toContain("HTTP 500");
    }
  });

  it("tolerates a completely empty (non-JSON) error body", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(new Response("", { status: 503 }));
    try {
      await api("/x");
      throw new Error("expected ApiError");
    } catch (e) {
      expect((e as ApiError).code).toBe("UNKNOWN");
      expect((e as ApiError).status).toBe(503);
    }
  });

  it("maps a network failure to NETWORK_ERROR with status 0", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new TypeError("fetch failed"));
    try {
      await api("/x");
      throw new Error("expected ApiError");
    } catch (e) {
      expect((e as ApiError).code).toBe("NETWORK_ERROR");
      expect((e as ApiError).status).toBe(0);
    }
  });

  it("maps an abort/timeout DOMException to a distinct code", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new DOMException("aborted", "AbortError"));
    try {
      await api("/x");
      throw new Error("expected ApiError");
    } catch (e) {
      expect((e as ApiError).code).toBe("ABORTED");
    }
  });

  it("should include error code from response body", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          error: { code: "VALIDATION_ERROR", message: "Invalid input" },
        }),
        { status: 422 },
      ),
    );

    try {
      await api("/bad");
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      expect((e as ApiError).code).toBe("VALIDATION_ERROR");
      expect((e as ApiError).status).toBe(422);
    }
  });
});
