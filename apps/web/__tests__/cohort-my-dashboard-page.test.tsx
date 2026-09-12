import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1", cohortId: "c-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import MyDashboardPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/cohorts/[cohortId]/my-dashboard/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const DASH = {
  cohort: { id: "c-1", name: "Fall Cohort", description: null, status: "active", member_count: 10 },
  assigned_skills: [
    {
      skill_id: "s-1",
      name: "Prompting",
      status: "in_progress",
      exercises_done: 2,
      exercises_total: 5,
    },
  ],
  assigned_projects: [
    {
      project_id: "p-1",
      title: "Chatbot",
      submission_status: "approved",
      score: 88,
      submitted_at: "2026-09-01T00:00:00Z",
      is_overdue: false,
    },
    {
      project_id: "p-2",
      title: "Late One",
      submission_status: "draft",
      score: null,
      submitted_at: null,
      is_overdue: true,
    },
  ],
  needs_revision: [
    { submission_id: "sub-1", project_id: "p-3", updated_at: "2026-09-01T00:00:00Z" },
  ],
  pending_peer_reviews: [
    { assessment_id: "a-1", submission_id: "sub-2", assigned_at: "2026-09-01T00:00:00Z" },
  ],
  recent_feedback: [
    {
      review_id: "r-1",
      submission_id: "sub-1",
      score: 90,
      feedback: "Great work",
      created_at: "2026-09-01T00:00:00Z",
      reviewer_type: "instructor",
    },
    {
      review_id: "r-2",
      submission_id: "sub-2",
      score: null,
      feedback: "Auto note",
      created_at: "2026-09-02T00:00:00Z",
      reviewer_type: "ai",
    },
  ],
  last_active_at: "2026-09-02T00:00:00Z",
};

function route(dash: Record<string, unknown> | null, cohorts: unknown[] = []) {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path.endsWith("/my-dashboard")) return Promise.resolve({ data: dash });
    if (path.endsWith("/my-cohorts")) return Promise.resolve({ data: cohorts });
    return Promise.resolve({ data: null });
  });
}

beforeEach(() => vi.clearAllMocks());

describe("MyDashboardPage (R455)", () => {
  it("renders skills, projects (overdue + score), feedback with reviewer emoji", async () => {
    route(DASH);
    render(<MyDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Fall Cohort");
    const body = document.body.textContent ?? "";
    expect(body).toContain("Prompting");
    expect(body).toContain("2/5 exercises");
    expect(body).toContain("Chatbot");
    expect(body).toContain("88 pts");
    expect(body).toContain("Overdue"); // p-2 is_overdue
    expect(body).toContain("Great work"); // instructor feedback
    expect(body).toContain("👤 Instructor");
    expect(body).toContain("🤖 AI Review"); // ai reviewer
    expect(body).toContain("90 pts"); // scored feedback
    // needs_revision + pending peer sections render when non-empty
    expect(body).toContain("Pending Peer Reviews");
  });

  it("empty optional sections are hidden entirely", async () => {
    route({ ...DASH, needs_revision: [], pending_peer_reviews: [], recent_feedback: [] });
    render(<MyDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Fall Cohort");
    const body = document.body.textContent ?? "";
    expect(body).not.toContain("Pending Peer Reviews");
    expect(body).not.toContain("AI Review");
  });

  it("cohort switcher lists OTHER cohorts only", async () => {
    route(DASH, [
      { id: "c-1", name: "Fall Cohort", status: "active" }, // current — excluded
      { id: "c-2", name: "Spring Cohort", status: "active" },
    ]);
    render(<MyDashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Fall Cohort");
    await waitFor(() => expect(screen.getByRole("combobox")).toBeTruthy());
    const options = Array.from(document.querySelectorAll("option")).map((o) => o.textContent);
    expect(options).toContain("Spring Cohort");
    // the current cohort is not an option to switch to
    expect(options.filter((o) => o === "Fall Cohort")).toEqual([]);
  });

  it("error state explains possible non-membership", async () => {
    api.mockImplementation(() => Promise.reject(new Error("nope")));
    render(<MyDashboardPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toMatch(/Failed to load dashboard/));
  });
});
