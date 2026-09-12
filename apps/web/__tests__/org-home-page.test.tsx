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

import OrgOverviewPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const ORG = {
  id: "o-1",
  name: "Acme Studio",
  slug: "acme",
  description: "We make things",
  role: "owner",
  member_count: 7,
  status: "active",
  settings: {},
  created_at: "2026-09-01T00:00:00Z",
};

beforeEach(() => vi.clearAllMocks());

describe("OrgOverviewPage (R469)", () => {
  it("owner sees stats, description, and BOTH Manage Members and Settings links", async () => {
    api.mockResolvedValue({ data: ORG });
    render(<OrgOverviewPage />, { wrapper: wrapper() });
    await screen.findByText("Acme Studio");
    expect(screen.getByText("We make things")).toBeTruthy();
    expect(screen.getByText("7")).toBeTruthy(); // member_count
    expect(screen.getByText("owner")).toBeTruthy();
    expect(screen.getByText("active")).toBeTruthy();
    expect(screen.getByText("Manage Members").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/members",
    );
    expect(screen.getByText("Settings").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/settings",
    );
  });

  it("admin also sees Settings; plain member does NOT", async () => {
    api.mockResolvedValue({ data: { ...ORG, role: "admin" } });
    const first = render(<OrgOverviewPage />, { wrapper: wrapper() });
    await screen.findByText("Acme Studio");
    expect(screen.getByText("Settings")).toBeTruthy();
    first.unmount();

    vi.clearAllMocks();
    api.mockResolvedValue({ data: { ...ORG, role: "member" } });
    render(<OrgOverviewPage />, { wrapper: wrapper() });
    await screen.findByText("Acme Studio");
    expect(screen.queryByText("Settings")).toBeNull(); // role gate
    expect(screen.getByText("Manage Members")).toBeTruthy(); // ungated
  });

  it("null description renders no description paragraph; error state surfaces", async () => {
    api.mockResolvedValue({ data: { ...ORG, description: null } });
    const first = render(<OrgOverviewPage />, { wrapper: wrapper() });
    await screen.findByText("Acme Studio");
    expect(screen.queryByText("We make things")).toBeNull();
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("org down"));
    render(<OrgOverviewPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toContain("Failed to load organization"));
  });
});
