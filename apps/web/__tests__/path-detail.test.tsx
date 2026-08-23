import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "org-1", pathId: "path-1" }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import PathDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/paths/[pathId]/page";
import { apiWithAuth } from "@/lib/api";

const mockApiWithAuth = vi.mocked(apiWithAuth);

const PATH_DETAIL = {
  id: "path-1",
  name: "Frontend Mastery",
  slug: "frontend-mastery",
  description: "A complete frontend learning path",
  status: "draft",
  estimated_minutes: 240,
  created_at: "2026-01-01T00:00:00Z",
};

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

function setupMocks() {
  mockApiWithAuth.mockImplementation((path: string) => {
    if (typeof path === "string" && path === "/orgs/org-1/paths/path-1") {
      return Promise.resolve({ data: PATH_DETAIL });
    }
    if (typeof path === "string" && path.includes("/items")) {
      return Promise.resolve({ data: [] });
    }
    return Promise.resolve({ data: [] });
  });
}

describe("PathDetailPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<PathDetailPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("shows error state on failure", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("fail"));
    render(<PathDetailPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/Failed to load path/),
    ).toBeDefined();
  });

  it("renders path name and status", async () => {
    setupMocks();
    render(<PathDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByDisplayValue("Frontend Mastery")).toBeDefined();
    expect(screen.getByText("draft")).toBeDefined();
  });

  it("renders path description", async () => {
    setupMocks();
    render(<PathDetailPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText("A complete frontend learning path"),
    ).toBeDefined();
  });

  it("renders Path Items section with empty state", async () => {
    setupMocks();
    render(<PathDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Path Items")).toBeDefined();
    expect(
      screen.getByText(/No items yet/),
    ).toBeDefined();
  });

  it("renders Add Item form", async () => {
    setupMocks();
    render(<PathDetailPage />, { wrapper: createWrapper() });
    // "Add Item" appears both as heading and button text
    const matches = await screen.findAllByText("Add Item");
    expect(matches.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Type")).toBeDefined();
  });

  it("renders Publish button for draft paths", async () => {
    setupMocks();
    render(<PathDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Publish")).toBeDefined();
  });

  it("renders Archive button", async () => {
    setupMocks();
    render(<PathDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Archive")).toBeDefined();
  });

  it("renders path items when present", async () => {
    mockApiWithAuth.mockImplementation((path: string) => {
      if (typeof path === "string" && path === "/orgs/org-1/paths/path-1") {
        return Promise.resolve({ data: PATH_DETAIL });
      }
      if (typeof path === "string" && path.includes("/items")) {
        return Promise.resolve({
          data: [
            {
              id: "item-1",
              item_type: "section",
              section_title: "Week 1",
              sort_order: 0,
              required: false,
            },
            {
              id: "item-2",
              item_type: "skill",
              skill_id: "sk-1",
              sort_order: 1,
              required: true,
            },
          ],
        });
      }
      if (typeof path === "string" && path.includes("/skills")) {
        return Promise.resolve({
          data: [{ id: "sk-1", name: "HTML Basics" }],
        });
      }
      return Promise.resolve({ data: [] });
    });
    render(<PathDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Week 1")).toBeDefined();
  });
});
