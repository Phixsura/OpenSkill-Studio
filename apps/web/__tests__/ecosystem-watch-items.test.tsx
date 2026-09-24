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
    if (path === `/ecosystem/watchlists/${LIST_ID}/items` && !init)
      return Promise.resolve({
        data: [
          {
            id: "I".repeat(26),
            target_kind: "github_repo",
            target_id: null,
            target_ref: "vendor/model-repo",
          },
        ],
      });
    return Promise.resolve({ data: [] });
  });
});

async function openList() {
  render(<WatchlistsPage />, { wrapper: wrapper() });
  fireEvent.click(await screen.findByText("Default"));
  // item panel loads
  expect(await screen.findByText(/vendor\/model-repo/)).toBeDefined();
}

describe("Watch item add/remove (ADR-016 §24 UI)", () => {
  it("Watch button POSTs the selected kind + ref to the items endpoint", async () => {
    await openList();
    fireEvent.change(screen.getByLabelText("Watch target kind"), {
      target: { value: "github_repo" },
    });
    fireEvent.change(screen.getByPlaceholderText(/external ref/), {
      target: { value: "acme/new-repo" },
    });
    fireEvent.click(screen.getByText("Watch"));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === `/ecosystem/watchlists/${LIST_ID}/items` &&
        (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(body.target_kind).toBe("github_repo");
    expect(body.target_ref).toBe("acme/new-repo");
    expect(body.target_id).toBeNull();
  });

  it("remove link DELETEs the specific item", async () => {
    await openList();
    fireEvent.click(screen.getByText("remove"));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          c[0] === `/ecosystem/watchlists/${LIST_ID}/items/${"I".repeat(26)}` &&
          (c[1] as RequestInit)?.method === "DELETE",
      ),
    ).toBe(true);
  });
});
