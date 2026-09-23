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
  usePathname: () => "/dashboard/ecosystem/watchlists",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import WatchlistsPage from "@/app/(dashboard)/dashboard/ecosystem/watchlists/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const LIST_ID = "W".repeat(26);

beforeEach(() => {
  vi.clearAllMocks();
  api.mockImplementation((path: string, init?: RequestInit) => {
    if (path === "/ecosystem/watchlists" && !init)
      return Promise.resolve({
        data: [
          {
            id: LIST_ID,
            name: "Default",
            min_severity: "info",
            muted_until: null,
            created_at: "2026-09-20T00:00:00Z",
          },
        ],
      });
    return Promise.resolve({ data: [] });
  });
});

describe("Watchlist noise controls (ADR-016 §24 UI)", () => {
  it("changing the severity threshold PATCHes min_severity", async () => {
    render(<WatchlistsPage />, { wrapper: wrapper() });
    const select = await screen.findByTitle("Only notify at/above this severity");
    fireEvent.change(select, { target: { value: "breaking" } });
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === `/ecosystem/watchlists/${LIST_ID}` && (c[1] as RequestInit)?.method === "PATCH",
    );
    expect(call).toBeDefined();
    expect(JSON.parse((call![1] as RequestInit).body as string).min_severity).toBe("breaking");
  });

  it("mute button PATCHes a muted_until timestamp", async () => {
    render(<WatchlistsPage />, { wrapper: wrapper() });
    const mute = await screen.findByLabelText("Mute notifications for 7 days");
    fireEvent.click(mute);
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === `/ecosystem/watchlists/${LIST_ID}` && (c[1] as RequestInit)?.method === "PATCH",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(typeof body.muted_until).toBe("string");
    expect(new Date(body.muted_until).getTime()).toBeGreaterThan(Date.now());
  });
});
