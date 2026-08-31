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

import WorkflowPackListPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/workflow-packs/page";
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

describe("WorkflowPackListPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading and new pack link", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<WorkflowPackListPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Workflow Packs")).toBeDefined();
    expect(screen.getByText("New Workflow Pack")).toBeDefined();
  });

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<WorkflowPackListPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("renders pack cards when loaded", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        {
          id: "wp1",
          name: "Hero Image Workflow",
          slug: "hero-image",
          summary: "E-commerce hero production",
          status: "draft",
          visibility: "private",
          workflow_type: "production",
          capability_tags: ["image_generation"],
          install_count: 3,
          created_at: "2026-01-01T00:00:00Z",
        },
        {
          id: "wp2",
          name: "Storyboard Pipeline",
          slug: "storyboard",
          summary: "Storyboard to video",
          status: "published",
          visibility: "public",
          workflow_type: "pipeline",
          capability_tags: ["image_to_video"],
          install_count: 9,
          created_at: "2026-02-01T00:00:00Z",
        },
      ],
      meta: { total: 2, has_more: false },
    });
    render(<WorkflowPackListPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Hero Image Workflow")).toBeDefined();
    expect(screen.getByText("Storyboard Pipeline")).toBeDefined();
    expect(screen.getByText("draft")).toBeDefined();
    expect(screen.getByText("published")).toBeDefined();
  });

  it("links new pack button to the correct URL", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<WorkflowPackListPage />, { wrapper: createWrapper() });
    const link = screen.getByText("New Workflow Pack").closest("a");
    expect(link?.getAttribute("href")).toBe("/dashboard/orgs/org-1/workflow-packs/new");
  });

  it("shows error message on failure", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("fail"));
    render(<WorkflowPackListPage />, { wrapper: createWrapper() });
    expect(await screen.findByText(/Failed to load workflow packs/)).toBeDefined();
  });
});
