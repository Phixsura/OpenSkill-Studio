import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import PlatformUsagePage from "@/app/(dashboard)/platform/usage/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const EVENT = {
  id: "u-1",
  tenant_id: "t-0123456789abc",
  org_id: "o-1",
  usage_type: "model_tokens",
  quantity: "1200.5",
  unit: "tokens",
  provider: "anthropic",
  model_or_service: "claude-sonnet-5",
  source: "workflow",
  occurred_at: "2026-09-01T10:00:00Z",
};

function route(capture: string[], opts?: { hasMore?: boolean }) {
  api.mockImplementation((rawPath: unknown) => {
    capture.push(String(rawPath ?? ""));
    return Promise.resolve({
      data: [EVENT, { ...EVENT, id: "u-2", provider: null, model_or_service: null }],
      meta: { total: 2, has_more: opts?.hasMore ?? false },
    });
  });
}

beforeEach(() => {
  vi.useFakeTimers();
  api.mockReset();
});
afterEach(() => {
  vi.useRealTimers();
});

async function flushDebounce() {
  await vi.advanceTimersByTimeAsync(450);
}

describe("PlatformUsagePage (R408)", () => {
  it("renders rows: qty+unit, provider/model pair, null provider as em dash", async () => {
    const calls: string[] = [];
    route(calls);
    render(<PlatformUsagePage />, { wrapper: wrapper() });
    await flushDebounce();
    await vi.waitFor(() => {
      expect(screen.getAllByText("1200.5 tokens", { exact: false }).length).toBe(2);
    });
    const body = document.body.textContent ?? "";
    expect(body).toContain("anthropic / claude-sonnet-5");
    expect(body).toContain("—"); // u-2 has no provider
    expect(body).toContain("workflow");
  });

  it("debounces filters 400ms, TRIMS usage_type/source, and resets to page 1", async () => {
    const calls: string[] = [];
    route(calls, { hasMore: true });
    render(<PlatformUsagePage />, { wrapper: wrapper() });
    await flushDebounce();
    await vi.waitFor(() => expect(calls.length).toBeGreaterThan(0));
    // go to page 2
    fireEvent.click(screen.getByRole("button", { name: "Next" }));
    await vi.waitFor(() => expect(calls.some((c) => c.includes("page=2"))).toBe(true));
    const before = calls.length;
    // type with trailing whitespace — nothing fires before the debounce window
    fireEvent.change(screen.getByPlaceholderText("Usage type"), {
      target: { value: "model_tokens  " },
    });
    fireEvent.change(screen.getByPlaceholderText("Source"), {
      target: { value: " workflow " },
    });
    await vi.advanceTimersByTimeAsync(200);
    expect(calls.length).toBe(before); // still inside the debounce window
    await vi.advanceTimersByTimeAsync(300);
    await vi.waitFor(() => {
      const last = calls[calls.length - 1];
      expect(last).toContain("usage_type=model_tokens"); // trimmed
      expect(last).not.toContain("model_tokens++"); // no encoded trailing spaces
      expect(last).toContain("source=workflow");
      expect(last).toContain("page=1"); // filter change resets the page
    });
  });

  it("Prev is disabled on page 1; Next disabled without has_more", async () => {
    const calls: string[] = [];
    route(calls, { hasMore: false });
    render(<PlatformUsagePage />, { wrapper: wrapper() });
    await flushDebounce();
    await vi.waitFor(() => expect(screen.getByText("Page 1")).toBeTruthy());
    expect((screen.getByRole("button", { name: "Prev" }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByRole("button", { name: "Next" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("backend errors surface via QueryError, not an empty table", async () => {
    api.mockImplementation(() => Promise.reject(new Error("bad filter")));
    render(<PlatformUsagePage />, { wrapper: wrapper() });
    await flushDebounce();
    await vi.waitFor(() => {
      expect(document.body.textContent).toMatch(/usage events/i);
      expect(document.body.textContent).toMatch(/failed|error|bad filter/i);
    });
  });
});
