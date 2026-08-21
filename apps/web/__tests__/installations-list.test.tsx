import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "org-1" }),
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import InstallationsListPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/installations/page";
import { apiWithAuth } from "@/lib/api";

const mockApiWithAuth = vi.mocked(apiWithAuth);

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("InstallationsListPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<InstallationsListPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Installed Packs")).toBeDefined();
  });

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<InstallationsListPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("renders installation table when loaded", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        {
          id: "i1",
          org_id: "org-1",
          pack_id: "pack-abc123xyz",
          release_id: "rel-1",
          installed_version: "1.2.0",
          status: "active",
          installed_by: "user1",
          installed_at: "2026-03-15T10:00:00Z",
        },
      ],
      meta: { total: 1 },
    });
    render(<InstallationsListPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("1.2.0")).toBeDefined();
    expect(screen.getByText("active")).toBeDefined();
    expect(screen.getByText("Pack")).toBeDefined();
    expect(screen.getByText("Version")).toBeDefined();
    expect(screen.getByText("Status")).toBeDefined();
  });

  it("shows error message on failure", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("fail"));
    render(<InstallationsListPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/Failed to load installations/),
    ).toBeDefined();
  });

  it("shows empty state when no installations", async () => {
    mockApiWithAuth.mockResolvedValue({ data: [], meta: { total: 0 } });
    render(<InstallationsListPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/No packs installed yet/),
    ).toBeDefined();
  });

  it("shows pack_name when available", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        {
          id: "i1",
          org_id: "org-1",
          pack_id: "pack-abc123xyz456",
          pack_name: "My Awesome Pack",
          release_id: "rel-1",
          installed_version: "1.0.0",
          status: "active",
          installed_by: "user1",
          installed_at: "2026-01-01T00:00:00Z",
        },
      ],
      meta: { total: 1 },
    });
    render(<InstallationsListPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("My Awesome Pack")).toBeDefined();
  });
});
