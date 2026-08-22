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

import PathsListPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/paths/page";
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

describe("PathsListPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and new path link", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<PathsListPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Learning Paths")).toBeDefined();
    expect(screen.getByText("New Path")).toBeDefined();
  });

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<PathsListPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("renders path cards when loaded", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        {
          id: "path-1",
          name: "Frontend Basics",
          slug: "frontend-basics",
          description: "Learn HTML, CSS, JS",
          status: "published",
          estimated_minutes: 120,
          created_at: "2026-01-01T00:00:00Z",
        },
      ],
      meta: { total: 1 },
    });
    render(<PathsListPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Frontend Basics")).toBeDefined();
    expect(screen.getByText("Learn HTML, CSS, JS")).toBeDefined();
    expect(screen.getByText("published")).toBeDefined();
    expect(screen.getByText("120 min")).toBeDefined();
  });

  it("shows error message on failure", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("fail"));
    render(<PathsListPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/Failed to load learning paths/),
    ).toBeDefined();
  });

  it("shows empty state when no paths", async () => {
    mockApiWithAuth.mockResolvedValue({ data: [], meta: { total: 0 } });
    render(<PathsListPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/No learning paths yet/),
    ).toBeDefined();
  });

  it("links new path button to correct URL", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<PathsListPage />, { wrapper: createWrapper() });
    const link = screen.getByText("New Path").closest("a");
    expect(link?.getAttribute("href")).toBe(
      "/dashboard/orgs/org-1/paths/new",
    );
  });

  it("shows no estimate text when estimated_minutes is 0", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        {
          id: "path-2",
          name: "Quick Path",
          slug: "quick",
          description: "A quick path",
          status: "draft",
          estimated_minutes: 0,
          created_at: "2026-02-01T00:00:00Z",
        },
      ],
      meta: { total: 1 },
    });
    render(<PathsListPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("No estimate")).toBeDefined();
  });
});
