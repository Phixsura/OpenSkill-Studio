import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1" }) }));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ReviewQueuePage from "@/app/(dashboard)/dashboard/orgs/[orgId]/packs/review-queue/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PACKS = [
  {
    id: "pk-1",
    name: "Pending Pack",
    summary: "s",
    review_status: "pending",
    created_at: "2026-09-01T00:00:00Z",
  },
  {
    id: "pk-2",
    name: "Approved Pack",
    summary: null,
    review_status: "approved",
    created_at: "2026-09-01T00:00:00Z",
  },
  {
    id: "pk-3",
    name: "Unreviewed Pack",
    summary: null,
    review_status: null,
    created_at: "2026-09-01T00:00:00Z",
  },
];

function route(posts: { path: string; body: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    if (init?.method === "POST") {
      posts.push({ path: String(rawPath ?? ""), body: init.body ? JSON.parse(init.body) : {} });
      return Promise.resolve({ data: {} });
    }
    return Promise.resolve({ data: PACKS });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());
afterEach(() => vi.unstubAllGlobals());

describe("ReviewQueuePage (R458)", () => {
  it("shows ONLY review_status=pending packs", async () => {
    route([]);
    render(<ReviewQueuePage />, { wrapper: wrapper() });
    await screen.findByText("Pending Pack");
    expect(screen.queryByText("Approved Pack")).toBeNull();
    expect(screen.queryByText("Unreviewed Pack")).toBeNull();
  });

  it("approve posts to the pack's approve endpoint", async () => {
    const posts: { path: string; body: unknown }[] = [];
    route(posts);
    render(<ReviewQueuePage />, { wrapper: wrapper() });
    await screen.findByText("Pending Pack");
    fireEvent.click(screen.getByRole("button", { name: /Approve/ }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/o-1/packs/pk-1/approve");
    await waitFor(() => expect(toasts.success).toHaveBeenCalledWith("Pack approved"));
  });

  it("reject requires a non-blank reason: cancel posts nothing, blank errors, real reason posts trimmed", async () => {
    const posts: { path: string; body: unknown }[] = [];
    route(posts);
    render(<ReviewQueuePage />, { wrapper: wrapper() });
    await screen.findByText("Pending Pack");

    // cancel → nothing posted, no error
    vi.stubGlobal(
      "prompt",
      vi.fn(() => null),
    );
    fireEvent.click(screen.getByRole("button", { name: /Reject/ }));
    expect(posts.length).toBe(0);
    expect(toasts.error).not.toHaveBeenCalled();

    // blank → error toast, nothing posted
    vi.stubGlobal(
      "prompt",
      vi.fn(() => "   "),
    );
    fireEvent.click(screen.getByRole("button", { name: /Reject/ }));
    expect(posts.length).toBe(0);
    expect(toasts.error).toHaveBeenCalledWith("A reason is required to reject a pack");

    // a real reason → posted TRIMMED
    vi.stubGlobal(
      "prompt",
      vi.fn(() => "  low quality  "),
    );
    fireEvent.click(screen.getByRole("button", { name: /Reject/ }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/o-1/packs/pk-1/reject");
    expect(posts[0]?.body).toEqual({ reason: "low quality" });
  });

  it("empty queue and error states", async () => {
    api.mockResolvedValue({ data: [PACKS[1]] }); // approved only → filtered out
    render(<ReviewQueuePage />, { wrapper: wrapper() });
    expect(await screen.findByText("No packs pending review.")).toBeTruthy();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("packs down"));
    render(<ReviewQueuePage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toMatch(/Failed to load packs/));
  });
});
