import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem/changes",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ChangesPage from "@/app/(dashboard)/dashboard/ecosystem/changes/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function change(id: string, field: string) {
  return {
    id,
    change_type: "price",
    field,
    old_value: null,
    new_value: { value: 1 },
    severity: "info",
    entity_kind: "model",
    detected_at: "2026-09-20T00:00:00Z",
    acknowledged: false,
  };
}

beforeEach(() => vi.clearAllMocks());

describe("Change feed cursor + acknowledge (ADR-016 §19 UI)", () => {
  it("loads the next page via the cursor and appends rows", async () => {
    api.mockImplementation((path: string) => {
      if (path.includes("cursor=CUR1"))
        return Promise.resolve({
          data: [change("c2", "page-two-field")],
          meta: { has_more: false, next_cursor: null },
        });
      if (path.startsWith("/ecosystem/changes"))
        return Promise.resolve({
          data: [change("c1", "page-one-field")],
          meta: { has_more: true, next_cursor: "CUR1" },
        });
      return Promise.resolve({ data: [] });
    });
    render(<ChangesPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/page-one-field/)).toBeDefined();
    fireEvent.click(screen.getByText("Load more (cursor)"));
    expect(await screen.findByText(/page-two-field/)).toBeDefined();
    // First page stays appended, button gone (has_more false)
    expect(screen.getByText(/page-one-field/)).toBeDefined();
    expect(screen.queryByText("Load more (cursor)")).toBeNull();
  });

  it("acknowledge POSTs to the change endpoint", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/changes?"))
        return Promise.resolve({
          data: [change("c9", "ack-me")],
          meta: { has_more: false, next_cursor: null },
        });
      return Promise.resolve({ data: [] });
    });
    render(<ChangesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Acknowledge"));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          c[0] === "/ecosystem/changes/c9/acknowledge" && (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
  });
});
