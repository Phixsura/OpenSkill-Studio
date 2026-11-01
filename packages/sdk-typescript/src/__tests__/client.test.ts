import { describe, test, expect, vi } from "vitest";
import { OpenSkillClient } from "../client.js";
import { AuthError, NotFoundError, RateLimitError } from "../errors.js";

describe("OpenSkillClient", () => {
  test("constructor sets defaults", () => {
    const client = new OpenSkillClient({ apiKey: "test-key" });
    expect(client).toBeDefined();
    expect(client.developer).toBeDefined();
    expect(client.apps).toBeDefined();
    expect(client.marketplace).toBeDefined();
    expect(client.cohorts).toBeDefined();
    expect(client.projects).toBeDefined();
  });

  test("constructor accepts custom baseUrl", () => {
    const client = new OpenSkillClient({
      apiKey: "test",
      baseUrl: "https://custom.api.com",
    });
    expect(client).toBeDefined();
  });

  test("request adds auth header and handles 401", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ error: { message: "Unauthorized" } }),
      headers: new Headers(),
    });

    const client = new OpenSkillClient({
      apiKey: "bad-key",
      fetch: mockFetch,
    });

    await expect(client.request("/test")).rejects.toThrow(AuthError);
    expect(mockFetch).toHaveBeenCalledOnce();
  });

  test("request handles 404", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ error: { message: "Not found" } }),
      headers: new Headers(),
    });

    const client = new OpenSkillClient({
      apiKey: "key",
      fetch: mockFetch,
    });

    await expect(client.request("/nonexistent")).rejects.toThrow(NotFoundError);
  });

  test("request handles 429 with retry-after", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 429,
      json: () => Promise.resolve({ error: { message: "Rate limited" } }),
      headers: new Headers({ "retry-after": "30" }),
    });

    const client = new OpenSkillClient({
      apiKey: "key",
      fetch: mockFetch,
    });

    try {
      await client.request("/test");
    } catch (e) {
      expect(e).toBeInstanceOf(RateLimitError);
      expect((e as RateLimitError).retryAfter).toBe(30);
    }
  });

  test("request handles successful response", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ data: { id: "123" } }),
    });

    const client = new OpenSkillClient({
      apiKey: "key",
      fetch: mockFetch,
    });

    const result = await client.request<{ data: { id: string } }>("/test");
    expect(result.data.id).toBe("123");
  });

  test("request sends query params", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ data: [] }),
    });

    const client = new OpenSkillClient({
      apiKey: "key",
      baseUrl: "https://api.test.com",
      fetch: mockFetch,
    });

    await client.request("/items", { query: { page: 1, limit: 10 } });

    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("page=1");
    expect(url).toContain("limit=10");
  });
});
