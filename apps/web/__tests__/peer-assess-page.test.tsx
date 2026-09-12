import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const routerPush = vi.hoisted(() => vi.fn());
vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1", projectId: "p-1", assessmentId: "a-1" }),
  useRouter: () => ({ push: routerPush }),
  useSearchParams: () => new URLSearchParams("submission=sub-1"),
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

import PeerAssessPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/projects/[projectId]/peer-assess/[assessmentId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PROJECT = {
  id: "p-1",
  title: "Chatbot",
  max_score: 100,
  rubric: [
    { criterion: "Quality", max_score: 60 },
    { criterion: "Docs", max_score: 40 },
  ],
};

function route(posts: { body: unknown }[]) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      posts.push({ body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({ data: {} });
    }
    if (path.includes("/submissions/")) return Promise.resolve({ data: { items: [] } });
    if (path.includes("/projects/")) return Promise.resolve({ data: PROJECT });
    return Promise.resolve({ data: null });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("PeerAssessPage (R459)", () => {
  it("the running total clamps each criterion at its max", async () => {
    route([]);
    render(<PeerAssessPage />, { wrapper: wrapper() });
    await screen.findByText("Quality");
    const inputs = screen.getAllByRole("spinbutton");
    fireEvent.change(inputs[0] as HTMLElement, { target: { value: "999" } }); // over 60
    fireEvent.change(inputs[1] as HTMLElement, { target: { value: "10" } });
    // display total clamps Quality to 60 → 70 total
    await waitFor(() => expect(document.body.textContent).toContain("70 / 100"));
  });

  it("submit is blocked with an inline error when a score is out of range", async () => {
    const posts: { body: unknown }[] = [];
    route(posts);
    render(<PeerAssessPage />, { wrapper: wrapper() });
    await screen.findByText("Quality");
    const inputs = screen.getAllByRole("spinbutton");
    fireEvent.change(inputs[0] as HTMLElement, { target: { value: "61" } }); // > max 60
    fireEvent.change(inputs[1] as HTMLElement, { target: { value: "10" } });
    fireEvent.click(screen.getByRole("button", { name: /Submit review/ }));
    expect(await screen.findByText(/Enter a score between 0 and 60/)).toBeTruthy();
    expect(posts.length).toBe(0);
    // a missing score is also blocked
    fireEvent.change(inputs[0] as HTMLElement, { target: { value: "" } });
    fireEvent.click(screen.getByRole("button", { name: /Submit review/ }));
    expect(posts.length).toBe(0);
  });

  it("a valid submit posts total + per-criterion breakdown and routes back", async () => {
    const posts: { body: unknown }[] = [];
    route(posts);
    render(<PeerAssessPage />, { wrapper: wrapper() });
    await screen.findByText("Quality");
    const inputs = screen.getAllByRole("spinbutton");
    fireEvent.change(inputs[0] as HTMLElement, { target: { value: "50" } });
    fireEvent.change(inputs[1] as HTMLElement, { target: { value: "30" } });
    fireEvent.change(screen.getByPlaceholderText(/What works well/), {
      target: { value: "  solid  " },
    });
    fireEvent.click(screen.getByRole("button", { name: /Submit review/ }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.body).toEqual({
      score: 80,
      score_breakdown: [
        { criterion: "Quality", score: 50, max_score: 60 },
        { criterion: "Docs", score: 30, max_score: 40 },
      ],
      feedback: "solid", // trimmed
    });
    await waitFor(() =>
      expect(routerPush).toHaveBeenCalledWith("/dashboard/orgs/o-1/projects/p-1"),
    );
  });
});
