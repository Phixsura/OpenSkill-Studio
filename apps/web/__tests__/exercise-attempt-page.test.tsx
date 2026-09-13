import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1", skillId: "s-1", exerciseId: "ex-1" }),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ExercisePage from "@/app/(dashboard)/dashboard/orgs/[orgId]/skills/[skillId]/exercises/[exerciseId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const MCQ = {
  id: "ex-1",
  title: "Pick two",
  description: "d",
  type: "multiple_choice",
  config: {
    options: [
      { id: "a", text: "Option A" },
      { id: "b", text: "Option B" },
      { id: "c", text: "Option C" },
    ],
    multiple: true,
  },
  max_score: 10,
};
const SINGLE = { ...MCQ, config: { ...MCQ.config, multiple: false } };
const TEXT = { ...MCQ, type: "text_answer", config: {} };

function route(
  exercise: unknown,
  opts?: {
    posts?: { body: unknown }[];
    result?: Record<string, unknown>;
    attempts?: unknown[];
  },
) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      opts?.posts?.push({ body: JSON.parse(init.body ?? "{}") });
      return Promise.resolve({
        data: {
          id: "at-1",
          score: 10,
          is_correct: true,
          feedback: "Nice",
          graded_by: "auto",
          created_at: "2026-09-12T00:00:00Z",
          ...opts?.result,
        },
      });
    }
    if (path.endsWith("/attempts")) return Promise.resolve({ data: opts?.attempts ?? [] });
    return Promise.resolve({ data: exercise });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("ExercisePage (R489)", () => {
  it("multi-select MCQ toggles accumulate and un-toggle; submit posts {answer:{selected}}", async () => {
    const posts: { body: unknown }[] = [];
    route(MCQ, { posts });
    render(<ExercisePage />, { wrapper: wrapper() });
    await screen.findByText("Option A");
    fireEvent.click(screen.getByText("Option A"));
    fireEvent.click(screen.getByText("Option B"));
    fireEvent.click(screen.getByText("Option C"));
    fireEvent.click(screen.getByText("Option B")); // un-toggle
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.body).toEqual({ answer: { selected: ["a", "c"] } });
    // graded result banner
    expect(await screen.findByText(/✅ Correct! — 10\/10 pts/)).toBeTruthy();
    expect(screen.getByText("Nice")).toBeTruthy();
  });

  it("single-select MCQ replaces the selection instead of accumulating", async () => {
    const posts: { body: unknown }[] = [];
    route(SINGLE, { posts });
    render(<ExercisePage />, { wrapper: wrapper() });
    await screen.findByText("Option A");
    fireEvent.click(screen.getByText("Option A"));
    fireEvent.click(screen.getByText("Option B")); // replaces, not adds
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.body).toEqual({ answer: { selected: ["b"] } });
  });

  it("empty MCQ selection and blank text answers are blocked client-side", async () => {
    const posts: { body: unknown }[] = [];
    route(MCQ, { posts });
    const first = render(<ExercisePage />, { wrapper: wrapper() });
    await first.findByText("Option A");
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(await screen.findByText("Please select an answer.")).toBeTruthy();
    expect(posts.length).toBe(0);
    first.unmount();

    vi.clearAllMocks();
    route(TEXT, { posts });
    render(<ExercisePage />, { wrapper: wrapper() });
    await screen.findByPlaceholderText("Enter your answer...");
    fireEvent.change(screen.getByPlaceholderText("Enter your answer..."), {
      target: { value: "   " },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(await screen.findByText("Please enter your answer.")).toBeTruthy();
    expect(posts.length).toBe(0);
  });

  it("incorrect result renders red; pending-review attempts show no score", async () => {
    route(SINGLE, {
      posts: [],
      result: { score: 0, is_correct: false, feedback: null },
      attempts: [
        {
          id: "at-0",
          score: null,
          is_correct: null,
          feedback: null,
          graded_by: null,
          created_at: "2026-09-10T00:00:00Z",
        },
        {
          id: "at-2",
          score: 7,
          is_correct: true,
          feedback: "ok",
          graded_by: "auto",
          created_at: "2026-09-11T00:00:00Z",
        },
      ],
    });
    render(<ExercisePage />, { wrapper: wrapper() });
    await screen.findByText("Option A");
    fireEvent.click(screen.getByText("Option A"));
    fireEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(await screen.findByText(/❌ Incorrect — 0\/10 pts/)).toBeTruthy();
    // history: ungraded shows Pending review, graded shows score
    expect(screen.getByText("Pending review")).toBeTruthy();
    expect(screen.getByText("7/10")).toBeTruthy();
  });
});
