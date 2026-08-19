import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "org-1", cohortId: "cohort-1" }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import CohortPathsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/cohorts/[cohortId]/paths/page";
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

describe("CohortPathsPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<CohortPathsPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Learning Paths")).toBeDefined();
    expect(
      screen.getByText(/Assign published learning paths to this cohort/),
    ).toBeDefined();
  });

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<CohortPathsPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("renders assigned paths when loaded", async () => {
    mockApiWithAuth.mockImplementation((path: string) => {
      if (typeof path === "string" && path.includes("/cohorts/")) {
        return Promise.resolve({
          data: [
            {
              path_id: "path-1",
              path_name: "Frontend Basics",
              assigned_at: "2026-06-01T10:00:00Z",
            },
          ],
        });
      }
      return Promise.resolve({ data: [], meta: { total: 0 } });
    });
    render(<CohortPathsPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Frontend Basics")).toBeDefined();
  });

  it("shows empty state when no paths assigned", async () => {
    mockApiWithAuth.mockImplementation(() =>
      Promise.resolve({ data: [], meta: { total: 0 } }),
    );
    render(<CohortPathsPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/No learning paths assigned/),
    ).toBeDefined();
  });

  it("shows assign dropdown when available paths exist", async () => {
    mockApiWithAuth.mockImplementation((path: string) => {
      if (typeof path === "string" && path.includes("/cohorts/")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({
        data: [
          { id: "path-2", name: "Backend Intro", status: "published" },
        ],
        meta: { total: 1 },
      });
    });
    render(<CohortPathsPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Assign a path")).toBeDefined();
    expect(screen.getByText("Assign")).toBeDefined();
  });

  it("renders Remove button for assigned paths", async () => {
    mockApiWithAuth.mockImplementation((path: string) => {
      if (typeof path === "string" && path.includes("/cohorts/")) {
        return Promise.resolve({
          data: [
            {
              path_id: "path-1",
              path_name: "Test Path",
              assigned_at: "2026-01-01T00:00:00Z",
            },
          ],
        });
      }
      return Promise.resolve({ data: [], meta: { total: 0 } });
    });
    render(<CohortPathsPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Remove")).toBeDefined();
  });
});
