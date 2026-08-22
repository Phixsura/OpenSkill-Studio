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

import PackListPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/packs/page";
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

describe("PackListPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and new pack link", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<PackListPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Skill Packs")).toBeDefined();
    expect(screen.getByText("New Pack")).toBeDefined();
  });

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<PackListPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("renders pack cards when loaded", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        {
          id: "p1",
          name: "Design Pack",
          slug: "design",
          summary: "Design skills training",
          status: "draft",
          visibility: "private",
          install_count: 5,
          created_at: "2026-01-01T00:00:00Z",
        },
        {
          id: "p2",
          name: "Dev Pack",
          slug: "dev",
          summary: "Developer skills",
          status: "published",
          visibility: "public",
          install_count: 12,
          created_at: "2026-02-01T00:00:00Z",
        },
      ],
      meta: { total: 2 },
    });
    render(<PackListPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Design Pack")).toBeDefined();
    expect(screen.getByText("Dev Pack")).toBeDefined();
    expect(screen.getByText("Design skills training")).toBeDefined();
    expect(screen.getByText("draft")).toBeDefined();
    expect(screen.getByText("published")).toBeDefined();
  });

  it("shows error message on failure", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("fail"));
    render(<PackListPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/Failed to load skill packs/),
    ).toBeDefined();
  });

  it("shows empty state when no packs", async () => {
    mockApiWithAuth.mockResolvedValue({ data: [], meta: { total: 0 } });
    render(<PackListPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/No skill packs found/),
    ).toBeDefined();
  });

  it("links new pack button to correct URL", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<PackListPage />, { wrapper: createWrapper() });
    const newPackLink = screen.getByText("New Pack").closest("a");
    expect(newPackLink?.getAttribute("href")).toBe(
      "/dashboard/orgs/org-1/packs/new",
    );
  });

  it("renders status filter select", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<PackListPage />, { wrapper: createWrapper() });
    expect(screen.getByDisplayValue("All")).toBeDefined();
  });
});
