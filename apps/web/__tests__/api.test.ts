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
