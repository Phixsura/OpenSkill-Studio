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
  useParams: () => ({ orgId: "org-1", runId: "run-1" }),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import WorkflowRunDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/workflow-runs/[runId]/page";
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

const runDetail = {
  data: {
    id: "run-1",
    org_id: "org-1",
    pack_id: "wp1",
    release_id: "rel1",
    installation_id: "inst1",
    inputs: { topic: "hero image" },
    outputs: null,
    status: "waiting_review",
    error_code: null,
    error: null,
    created_at: "2026-08-23T00:00:00Z",
    started_at: "2026-08-23T00:00:01Z",
    finished_at: null,
    step_runs: [
      {
        id: "sr1",
        step_id: "build_prompt",
        step_type: "prompt_template",
        status: "completed",
        attempt: 1,
        max_attempts: 3,
        output: { prompt: "Write about hero image" },
        error_code: null,
        error: null,
        offering_id: null,
        started_at: "2026-08-23T00:00:01Z",
        finished_at: "2026-08-23T00:00:02Z",
      },
      {
        id: "sr2",
        step_id: "qa_gate",
        step_type: "review_gate",
        status: "waiting_review",
        attempt: 1,
        max_attempts: 3,
        output: null,
        error_code: null,
        error: null,
        offering_id: null,
        started_at: "2026-08-23T00:00:02Z",
        finished_at: null,
      },
    ],
    events: [
      { id: "ev1", step_id: null, event_type: "run_created", payload: {}, created_at: "2026-08-23T00:00:00Z" },
      { id: "ev2", step_id: "qa_gate", event_type: "review_requested", payload: {}, created_at: "2026-08-23T00:00:02Z" },
    ],
  },
};

const reviews = {
  data: [
    {
      id: "rev1",
      step_run_id: "sr2",
      org_id: "org-1",
      instructions: "Check quality",
      due_at: "2026-08-30T00:00:00Z",
      decision: null,
      decision_note: null,
      decided_by: null,
      decided_at: null,
      created_at: "2026-08-23T00:00:02Z",
    },
  ],
};

describe("WorkflowRunDetailPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading state", () => {
    mockApiWithAuth.mockReturnValue(new Promise(() => {}));
    render(<WorkflowRunDetailPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Loading...")).toBeDefined();
  });

  it("renders step timeline with step ids and statuses", async () => {
    mockApiWithAuth.mockImplementation((path: string) => {
      if (path.includes("/step-reviews")) return Promise.resolve(reviews);
      return Promise.resolve(runDetail);
    });
    render(<WorkflowRunDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("build_prompt")).toBeDefined();
    expect(screen.getByText("qa_gate")).toBeDefined();
    // Both statuses visible (run header + step badges may repeat waiting_review)
    expect(screen.getAllByText(/waiting_review/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/completed/).length).toBeGreaterThan(0);
  });

  it("renders the review decision section for waiting_review steps", async () => {
    mockApiWithAuth.mockImplementation((path: string) => {
      if (path.includes("/step-reviews")) return Promise.resolve(reviews);
      return Promise.resolve(runDetail);
    });
    render(<WorkflowRunDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText(/Review required/)).toBeDefined();
    expect(screen.getByText("Check quality")).toBeDefined();
    expect(screen.getByText("Approve")).toBeDefined();
    expect(screen.getByText("Reject")).toBeDefined();
  });

  it("shows error state when the run fails to load", async () => {
    mockApiWithAuth.mockRejectedValue(new Error("boom"));
    render(<WorkflowRunDetailPage />, { wrapper: createWrapper() });
    expect(await screen.findByText(/Failed to load run/)).toBeDefined();
  });
});
