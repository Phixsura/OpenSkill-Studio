import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import OpportunitiesPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/opportunities/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => vi.clearAllMocks());

describe("OpportunitiesPage (R452)", () => {
  it("brief cards: known type label mapped, unknown type falls back to raw, link to brief", async () => {
    api.mockResolvedValue({
      data: [
        {
          id: "b-1",
          title: "Hero Shots",
          client_name: "Acme",
          project_type: "product_visualization",
          objective: "Render the product",
          status: "open",
          created_at: "2026-09-01T00:00:00Z",
        },
        {
          id: "b-2",
          title: "Weird Job",
          client_name: "Beta",
          project_type: "custom_thing",
          objective: "Do the thing",
          status: "open",
          created_at: "2026-09-02T00:00:00Z",
        },
      ],
    });
    render(<OpportunitiesPage />, { wrapper: wrapper() });
    await screen.findByText("Hero Shots");
    const body = document.body.textContent ?? "";
    expect(body).toContain("Product Visualization"); // mapped label
    expect(body).toContain("custom_thing"); // unknown type -> raw
    expect(body).toContain("Acme");
    expect(screen.getByText("Hero Shots").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/briefs/b-1",
    );
  });

  it("empty state message when no open briefs", async () => {
    api.mockResolvedValue({ data: [] });
    render(<OpportunitiesPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/No open commercial projects/)).toBeTruthy();
  });

  it("fetch error surfaces the failure line", async () => {
    api.mockImplementation(() => Promise.reject(new Error("briefs down")));
    render(<OpportunitiesPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toMatch(/Failed to load opportunities/));
  });
});
