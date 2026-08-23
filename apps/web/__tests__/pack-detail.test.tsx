import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "org-1", packId: "pack-1" }),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import PackDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/packs/[packId]/page";
import { apiWithAuth } from "@/lib/api";

const mockApiWithAuth = vi.mocked(apiWithAuth);

const PACK = {
  id: "pack-1",
  name: "Design Skills",
  slug: "design-skills",
  summary: "Master design tools",
  description: "Full description here",
  status: "draft",
  visibility: "private",
  install_count: 3,
  difficulty: "beginner",
  estimated_minutes: 60,
  scenario_tags: ["ux"],
  tool_tags: ["figma"],
  learning_outcomes: ["Design UIs"],
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

function setupPackMock() {
  mockApiWithAuth.mockImplementation((path: string) => {
    if (typeof path === "string" && path === "/orgs/org-1/packs/pack-1") {
      return Promise.resolve({ data: PACK });
    }
    if (typeof path === "string" && path.includes("/analytics")) {
      return Promise.resolve({
        data: {
          install_count: 0,
          average_rating: null,
          review_count: 0,
          installs_by_version: [],
        },
      });
    }
    return Promise.resolve({ data: [] });
  });
}

describe("PackDetailPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<PackDetailPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("shows error state on failure", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("fail"));
    render(<PackDetailPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/Failed to load pack/),
    ).toBeDefined();
  });

  it("renders pack name and status badges", async () => {
    setupPackMock();
    render(<PackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Design Skills")).toBeDefined();
    expect(screen.getByText("draft")).toBeDefined();
    expect(screen.getByText("private")).toBeDefined();
  });

  it("renders pack summary and install count", async () => {
    setupPackMock();
    render(<PackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Master design tools")).toBeDefined();
    expect(screen.getByText(/3 install/)).toBeDefined();
  });

  it("renders Contents section headings", async () => {
    setupPackMock();
    render(<PackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Contents")).toBeDefined();
    expect(screen.getByText("Skills")).toBeDefined();
    expect(screen.getByText("Templates")).toBeDefined();
  });

  it("shows empty state for skills and templates", async () => {
    setupPackMock();
    render(<PackDetailPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText("No skills added yet."),
    ).toBeDefined();
    expect(screen.getByText("No templates added yet.")).toBeDefined();
  });

  it("renders Releases section", async () => {
    setupPackMock();
    render(<PackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Releases")).toBeDefined();
    expect(screen.getByText("No releases yet.")).toBeDefined();
  });

  it("renders Publish New Release form", async () => {
    setupPackMock();
    render(<PackDetailPage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText("Publish New Release"),
    ).toBeDefined();
    expect(screen.getByLabelText("Version")).toBeDefined();
    expect(screen.getByLabelText("Changelog")).toBeDefined();
    expect(screen.getByText("Publish")).toBeDefined();
  });

  it("renders visibility toggle button", async () => {
    setupPackMock();
    render(<PackDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Set Public")).toBeDefined();
  });
});
