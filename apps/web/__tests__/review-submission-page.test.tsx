import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const routerPush = vi.hoisted(() => vi.fn());
vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1", submissionId: "sub-1" }),
  useRouter: () => ({ push: routerPush }),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ReviewSubmissionPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/reviews/[submissionId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const SUB = {
  id: "sub-1",
  project_id: "p-1",
  version: 2,
  status: "submitted",
  is_late: true,
  items: [],
  reviews: [
    {
      id: "r-1",
      status: "revision_requested",
      score: null,
      feedback: "redo it",
      created_at: "2026-08-30T00:00:00Z",
    },
  ],
};

function route(posts: { body: unknown }[], maxScore = 100) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      posts.push({ body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: {} });
    }
    if (path.includes("/reviews/pending"))
      return Promise.resolve({ data: [{ id: "sub-1", project_id: "p-1" }], meta: { total: 1 } });
    if (path.includes("/submissions/sub-1")) return Promise.resolve({ data: SUB });
    if (path.includes("/comments")) return Promise.resolve({ data: [] });
    if (path.endsWith("/projects/p-1")) return Promise.resolve({ data: { max_score: maxScore } });
    return Promise.resolve({ data: null });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("ReviewSubmissionPage (R461)", () => {
  it("resolves the submission via the pending queue and shows version + late flag + prior reviews", async () => {
    route([]);
    render(<ReviewSubmissionPage />, { wrapper: wrapper() });
    await screen.findByText("Review Submission v2");
    const body = document.body.textContent ?? "";
    expect(body).toContain("Late submission");
    expect(body).toContain("redo it"); // prior review feedback
    expect(body).toContain("revision requested"); // underscores -> space
  });

  it("approve with an over-max score is blocked with an inline error, nothing posts", async () => {
    const posts: { body: unknown }[] = [];
    route(posts, 80);
    render(<ReviewSubmissionPage />, { wrapper: wrapper() });
    await screen.findByText("Review Submission v2");
    fireEvent.change(screen.getByRole("spinbutton"), { target: { value: "81" } });
    fireEvent.click(screen.getByRole("button", { name: /Approve/ }));
    expect(await screen.findByText("Score must be between 0 and 80")).toBeTruthy();
    expect(posts.length).toBe(0);
  });

  it("approve posts the parsed score + feedback and routes back to the queue", async () => {
    const posts: { body: unknown }[] = [];
    route(posts);
    render(<ReviewSubmissionPage />, { wrapper: wrapper() });
    await screen.findByText("Review Submission v2");
    fireEvent.change(screen.getByRole("spinbutton"), { target: { value: "88" } });
    fireEvent.change(screen.getByPlaceholderText(/constructive feedback/), {
      target: { value: "solid work" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Approve/ }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.body).toEqual({ status: "approved", score: 88, feedback: "solid work" });
    await waitFor(() => expect(routerPush).toHaveBeenCalledWith("/dashboard/orgs/o-1/reviews"));
  });

  it("request-revision and reject post their statuses without requiring a score", async () => {
    const posts: { body: unknown }[] = [];
    route(posts);
    render(<ReviewSubmissionPage />, { wrapper: wrapper() });
    await screen.findByText("Review Submission v2");
    fireEvent.click(screen.getByRole("button", { name: /Request Revision/ }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect((posts[0]?.body as { status: string }).status).toBe("revision_requested");
    expect("score" in (posts[0]?.body as object)).toBe(false); // blank score omitted
  });
});
