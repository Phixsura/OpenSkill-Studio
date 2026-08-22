import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "org-1" }),
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import ReviewQueuePage from "@/app/(dashboard)/dashboard/orgs/[orgId]/packs/review-queue/page";
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

describe("ReviewQueuePage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders heading", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<ReviewQueuePage />, { wrapper: createWrapper() });
    expect(screen.getByText("Review Queue")).toBeDefined();
  });

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<ReviewQueuePage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("shows error state", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("fail"));
    render(<ReviewQueuePage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/Failed to load packs/),
    ).toBeDefined();
  });

  it("shows empty state when no pending packs", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        { id: "p1", name: "Published Pack", review_status: "approved", status: "published" },
      ],
    });
    render(<ReviewQueuePage />, { wrapper: createWrapper() });
    expect(
      await screen.findByText(/No packs pending review/),
    ).toBeDefined();
  });

  it("renders pending packs with approve and reject buttons", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        {
          id: "p1",
          name: "Pending Pack",
          slug: "pending",
          summary: "Needs review",
          status: "published",
          visibility: "public",
          review_status: "pending",
          install_count: 0,
          created_at: "2026-06-15T10:00:00Z",
        },
      ],
    });
    render(<ReviewQueuePage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Pending Pack")).toBeDefined();
    expect(screen.getByText("Needs review")).toBeDefined();
    expect(screen.getByText("Approve")).toBeDefined();
    expect(screen.getByText("Reject")).toBeDefined();
  });

  it("filters out non-pending packs", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        { id: "p1", name: "Approved Pack", review_status: "approved", status: "published", created_at: "2026-01-01T00:00:00Z" },
        { id: "p2", name: "Pending Pack", review_status: "pending", status: "published", summary: "", created_at: "2026-01-02T00:00:00Z" },
        { id: "p3", name: "Rejected Pack", review_status: "rejected", status: "published", created_at: "2026-01-03T00:00:00Z" },
      ],
    });
    render(<ReviewQueuePage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Pending Pack")).toBeDefined();
    expect(screen.queryByText("Approved Pack")).toBeNull();
    expect(screen.queryByText("Rejected Pack")).toBeNull();
  });
});
