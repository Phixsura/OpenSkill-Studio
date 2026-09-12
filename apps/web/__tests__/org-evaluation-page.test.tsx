import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import EvaluationPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/evaluation/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const TASKS = [
  {
    id: "task-000000000001",
    type: "image_review",
    status: "completed",
    llm_model: "claude-sonnet-5",
    input_tokens: 100,
    output_tokens: 50,
    cost_usd: 0.1234,
    created_at: "2026-09-01T00:00:00Z",
  },
  {
    id: "task-000000000002",
    type: "prompt_eval",
    status: "failed",
    llm_model: null,
    input_tokens: null,
    output_tokens: null,
    cost_usd: null,
    created_at: "2026-09-02T00:00:00Z",
  },
];

function route(usage: Record<string, unknown> | null, total = 2) {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path.includes("/evaluation/tasks"))
      return Promise.resolve({ data: TASKS, meta: { total } });
    if (path.includes("/evaluation/usage")) return Promise.resolve({ data: usage });
    return Promise.resolve({ data: null });
  });
}

beforeEach(() => vi.clearAllMocks());

describe("EvaluationPage (R448)", () => {
  it("usage tiles: task count, cost to 2dp, budget remaining (null => Unlimited)", async () => {
    route({
      total_tasks: 7,
      total_cost_usd: 12.5,
      budget_usd: 100,
      budget_remaining: 87.5,
      month: "2026-09",
    });
    render(<EvaluationPage />, { wrapper: wrapper() });
    await screen.findByText("AI Evaluation");
    const body = document.body.textContent ?? "";
    expect(body).toContain("7");
    expect(body).toContain("$12.50");
    expect(body).toContain("$87.50");
  });

  it("null budget_remaining renders Unlimited", async () => {
    route({
      total_tasks: 1,
      total_cost_usd: 0.5,
      budget_usd: null,
      budget_remaining: null,
      month: "2026-09",
    });
    render(<EvaluationPage />, { wrapper: wrapper() });
    await screen.findByText("AI Evaluation");
    expect(screen.getByText("Unlimited")).toBeTruthy();
  });

  it("task rows: type emoji + label, status color, cost 4dp, null model/cost em dash", async () => {
    route(null);
    render(<EvaluationPage />, { wrapper: wrapper() });
    await screen.findByText("AI Evaluation");
    const body = document.body.textContent ?? "";
    expect(body).toContain("🖼️"); // image_review -> image emoji
    expect(body).toContain("image review"); // underscores -> spaces
    expect(body).toContain("✏️"); // prompt_eval -> prompt emoji
    expect(body).toContain("$0.1234"); // cost 4dp
    expect(body).toContain("claude-sonnet-5");
    expect(body).toContain("—"); // null model + null cost
    // status color class present on the completed row
    const completed = screen.getByText("completed");
    expect(completed.className).toContain("text-green-600");
    const failed = screen.getByText("failed");
    expect(failed.className).toContain("text-red-600");
  });

  it("truncation note when fewer than total; empty state otherwise", async () => {
    route(null, 10);
    render(<EvaluationPage />, { wrapper: wrapper() });
    await screen.findByText("AI Evaluation");
    expect(screen.getByText("Showing 2 of 10 tasks")).toBeTruthy();

    vi.clearAllMocks();
    api.mockImplementation((rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path.includes("/evaluation/tasks"))
        return Promise.resolve({ data: [], meta: { total: 0 } });
      return Promise.resolve({ data: null });
    });
    render(<EvaluationPage />, { wrapper: wrapper() });
    expect(await screen.findByText("No evaluation tasks yet.")).toBeTruthy();
  });

  it("task fetch error surfaces the retry message", async () => {
    api.mockImplementation(() => Promise.reject(new Error("eval down")));
    render(<EvaluationPage />, { wrapper: wrapper() });
    await waitFor(() => {
      expect(document.body.textContent).toMatch(/Failed to load evaluation tasks/);
    });
  });
});
