import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => {
  class MockApiError extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  }
  return { apiWithAuth: vi.fn(), ApiError: MockApiError };
});

import { PeerReviewSection } from "@/components/peer-review-section";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function round(over: Partial<Record<string, unknown>> = {}) {
  return {
    id: "rd-1",
    project_id: "p-1",
    name: "Peer Review",
    num_reviews: 2,
    anonymous: true,
    include_self_review: false,
    phase: "setup",
    deadline: null,
    created_at: "2026-09-01T00:00:00Z",
    ...over,
  };
}

function route(opts: {
  rounds?: unknown[];
  my?: unknown[];
  results?: unknown[];
  posts?: { path: string; body?: unknown }[];
  failPost?: boolean;
}) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      opts.posts?.push({ path, body: init.body ? JSON.parse(init.body) : undefined });
      if (opts.failPost) return Promise.reject(new Error("boom"));
      return Promise.resolve({ data: { id: "rd-new" } });
    }
    if (path.includes("my-assessments")) return Promise.resolve({ data: opts.my ?? [] });
    if (path.endsWith("/results")) return Promise.resolve({ data: opts.results ?? [] });
    return Promise.resolve({ data: opts.rounds ?? [] });
  }) as typeof apiWithAuth);
}

const props = { orgId: "o-1", projectId: "p-1", isInstructor: true };

beforeEach(() => vi.clearAllMocks());

describe("PeerReviewSection (R508)", () => {
  // EQUIVALENT-MUTANT NOTE: the function-level `if (busy) return` in
  // createRound/transition is UNREACHABLE through this UI — the buttons set
  // disabled={busy}, so RTL's second click never fires onClick. Removing the
  // function gate does NOT fail this test; it is defense-in-depth against
  // future non-button invocation paths (cf. CommentPanel's Enter-key path,
  // where the same gate IS load-bearing and mutation-proved in R504).
  it("create round posts trimmed name + parsed num_reviews + flags; double-click posts ONCE (R183)", async () => {
    const posts: { path: string; body?: unknown }[] = [];
    let resolve!: (v: { data: { id: string } }) => void;
    api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
      const path = String(rawPath ?? "");
      if (init?.method === "POST") {
        posts.push({ path, body: init.body ? JSON.parse(init.body) : undefined });
        return new Promise<{ data: { id: string } }>((r) => (resolve = r));
      }
      return Promise.resolve({ data: [] });
    }) as typeof apiWithAuth);
    render(<PeerReviewSection {...props} />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: "Set up peer review" }));
    fireEvent.change(screen.getByPlaceholderText("Round name"), {
      target: { value: "  Round A  " },
    });
    const num = screen.getByDisplayValue("2");
    fireEvent.change(num, { target: { value: "3" } });
    fireEvent.click(screen.getAllByRole("checkbox")[1] as HTMLElement); // include self-review
    const btn = screen.getByRole("button", { name: /Create round|Creating/ });
    fireEvent.click(btn);
    fireEvent.click(btn); // second click mid-flight
    resolve({ data: { id: "rd-new" } });
    await waitFor(() => expect(posts.length).toBe(1)); // busy gate held
    expect(posts[0]?.path).toBe("/orgs/o-1/peer-review-rounds");
    expect(posts[0]?.body).toEqual({
      project_id: "p-1",
      name: "Round A", // trimmed
      num_reviews: 3, // parsed int
      anonymous: true,
      include_self_review: true,
    });
  });

  it("phase controls: setup shows Allocate & start; assessment shows Close; POST hits the action path", async () => {
    const posts: { path: string; body?: unknown }[] = [];
    route({ rounds: [round()], posts });
    const first = render(<PeerReviewSection {...props} />, { wrapper: wrapper() });
    await first.findByText("Collecting submissions");
    fireEvent.click(screen.getByRole("button", { name: "Allocate & start" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/o-1/peer-review-rounds/rd-1/start");
    first.unmount();

    vi.clearAllMocks();
    const posts2: { path: string }[] = [];
    route({ rounds: [round({ phase: "assessment" })], posts: posts2 });
    render(<PeerReviewSection {...props} />, { wrapper: wrapper() });
    await screen.findByText("Peer review in progress");
    expect(screen.queryByRole("button", { name: "Allocate & start" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Close round" }));
    await waitFor(() => expect(posts2.length).toBe(1));
    expect(posts2[0]?.path).toBe("/orgs/o-1/peer-review-rounds/rd-1/close");
  });

  it("learner queue: done counter, pending rows link to peer-assess with submission+round params, self chip", async () => {
    route({
      rounds: [round({ phase: "assessment" })],
      my: [
        { id: "a-1", submission_id: "sub-1", is_self_review: false, status: "submitted", score: 8 },
        {
          id: "a-2",
          submission_id: "sub-2",
          is_self_review: false,
          status: "pending",
          score: null,
        },
        { id: "a-3", submission_id: "sub-3", is_self_review: true, status: "pending", score: null },
      ],
    });
    render(<PeerReviewSection {...props} isInstructor={false} />, { wrapper: wrapper() });
    await screen.findByText(/Your reviews \(1\/3 done\)/);
    expect(screen.getByText("✓ Reviewed")).toBeTruthy();
    const link = screen.getByText(/Review submission 2/).closest("a");
    expect(link?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/projects/p-1/peer-assess/a-2?submission=sub-2&round=rd-1",
    );
    expect(screen.getByText("Self-review →").closest("a")?.getAttribute("href")).toContain(
      "/peer-assess/a-3?submission=sub-3",
    );
    expect(screen.getByText("self")).toBeTruthy();
    // learners never see instructor phase controls
    expect(screen.queryByRole("button", { name: "Close round" })).toBeNull();
  });

  it("closed round renders the results table with null-score dash; non-instructor with no rounds renders nothing", async () => {
    route({
      rounds: [round({ phase: "closed" })],
      results: [
        { submission_id: "01ABCDEFGHIJKLMNOPQRSTUVWX", avg_score: 8.5, review_count: 3 },
        { submission_id: "01ABCDEFGHIJKLMNOPQRSTUVYZ", avg_score: null, review_count: 0 },
      ],
    });
    const first = render(<PeerReviewSection {...props} />, { wrapper: wrapper() });
    await first.findByText("Results");
    expect(screen.getByText("8.5")).toBeTruthy();
    expect(screen.getByText("—")).toBeTruthy(); // null avg
    expect(screen.getByText("QRSTUVWX")).toBeTruthy(); // last-8 slice
    first.unmount();

    vi.clearAllMocks();
    route({ rounds: [] });
    const { container } = render(<PeerReviewSection {...props} isInstructor={false} />, {
      wrapper: wrapper(),
    });
    await waitFor(() => expect(api).toHaveBeenCalled());
    await new Promise((r) => setTimeout(r, 20));
    expect(container.textContent).toBe(""); // learners see nothing without rounds
  });

  it("create failure surfaces the error and the form stays usable", async () => {
    const posts: { path: string }[] = [];
    route({ posts, failPost: true });
    render(<PeerReviewSection {...props} />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: "Set up peer review" }));
    fireEvent.click(screen.getByRole("button", { name: "Create round" }));
    expect(await screen.findByText("Failed to create round")).toBeTruthy();
    expect(
      (screen.getByRole("button", { name: "Create round" }) as HTMLButtonElement).disabled,
    ).toBe(false); // busy released
  });
});
