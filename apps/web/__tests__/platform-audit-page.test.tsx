import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import PlatformAuditPage from "@/app/(dashboard)/platform/audit/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const ULID_A = "01JACTORAAAAAAAAAAAAAAAAAA"; // 26 chars
const ULID_T = "01JTARGETBBBBBBBBBBBBBBBBB";

const EVENTS = [
  {
    id: "a-1",
    actor_user_id: ULID_A,
    actor_type: "platform",
    action: "tenant.suspended",
    target_type: "tenant",
    target_id: ULID_T,
    tenant_id: "t-1",
    reason: "fraud hold",
    after: { status: "suspended" },
    created_at: "2026-09-01T10:00:00Z",
  },
  {
    id: "a-2",
    actor_user_id: null,
    actor_type: "system",
    action: "invoice.issued",
    target_type: "invoice",
    target_id: ULID_T,
    tenant_id: "t-1",
    reason: null,
    after: { total_minor: 123456, currency: "EUR" },
    created_at: "2026-09-01T11:00:00Z",
  },
  {
    id: "a-3",
    actor_user_id: null,
    actor_type: "system",
    action: "outbox.swept",
    target_type: "outbox",
    target_id: ULID_T,
    tenant_id: null,
    reason: null,
    after: null,
    created_at: "2026-09-01T12:00:00Z",
  },
];

function route(capture: string[]) {
  api.mockImplementation((rawPath: unknown) => {
    capture.push(String(rawPath ?? ""));
    return Promise.resolve({ data: EVENTS, meta: { has_more: false } });
  });
}

beforeEach(() => {
  vi.useFakeTimers();
  api.mockReset();
});
afterEach(() => {
  vi.useRealTimers();
});

describe("PlatformAuditPage (R409)", () => {
  it("renders FULL 26-char ids (R101[L16] — no 10-char collisions) with hover titles", async () => {
    const calls: string[] = [];
    route(calls);
    render(<PlatformAuditPage />, { wrapper: wrapper() });
    await vi.advanceTimersByTimeAsync(450);
    await vi.waitFor(() => expect(screen.getByText("tenant.suspended")).toBeTruthy());
    // full ULID text, not a truncated slice
    expect(screen.getByText(ULID_A)).toBeTruthy();
    expect(screen.getByText(ULID_A).getAttribute("title")).toBe(ULID_A);
    // detail precedence: reason > after-JSON > em dash
    const body = document.body.textContent ?? "";
    expect(body).toContain("fraud hold");
    expect(body).toContain('{"total_minor":123456'); // a-2: reason null → after JSON
    expect(body).toContain("—"); // a-3: neither
    // actor cell: system rows without a user id render no separator dot
    expect(body).toContain("platform · ");
  });

  it("debounced filters land in ONE request with tenant_id + action and reset the page", async () => {
    const calls: string[] = [];
    route(calls);
    render(<PlatformAuditPage />, { wrapper: wrapper() });
    await vi.advanceTimersByTimeAsync(450);
    await vi.waitFor(() => expect(calls.length).toBeGreaterThan(0));
    const before = calls.length;
    fireEvent.change(screen.getByPlaceholderText("Tenant ID"), { target: { value: "t-9" } });
    fireEvent.change(screen.getByPlaceholderText("Action (e.g. tenant.suspended)"), {
      target: { value: "tenant.suspended" },
    });
    await vi.advanceTimersByTimeAsync(200);
    expect(calls.length).toBe(before); // inside the debounce window
    await vi.advanceTimersByTimeAsync(300);
    await vi.waitFor(() => {
      const last = calls[calls.length - 1];
      expect(last).toContain("tenant_id=t-9");
      expect(last).toContain("action=tenant.suspended");
      expect(last).toContain("page=1");
    });
  });

  it("query errors surface — an auditor can tell 'endpoint down' from 'no events'", async () => {
    api.mockImplementation(() => Promise.reject(new Error("audit down")));
    render(<PlatformAuditPage />, { wrapper: wrapper() });
    await vi.advanceTimersByTimeAsync(450);
    await vi.waitFor(() => {
      expect(document.body.textContent).toMatch(/audit events/i);
      expect(document.body.textContent).toMatch(/failed|error|down/i);
    });
  });
});
