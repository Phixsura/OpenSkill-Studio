import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1", cohortId: "c-1", userId: "u-1" }),
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import LearnerDrilldownPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/cohorts/[cohortId]/progress/[userId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const DRILL = {
  user_name: "Ada",
  skills: [
    {
      skill_id: "s-1",
      name: "Prompting",
      status: "in_progress",
      exercises_done: 2,
      exercises_total: 5,
    },
  ],
  projects: [
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
      title: "Overdue Draft",
      submission_status: "not_started",
      score: null,
      submitted_at: null,
      is_overdue: true,
    },
  ],
  last_active_at: null,
};

beforeEach(() => vi.clearAllMocks());

describe("LearnerDrilldownPage (R462)", () => {
  it("renders per-learner skills/projects with overdue chip, score, and 'Never' last-active", async () => {
    api.mockResolvedValue({ data: DRILL });
    render(<LearnerDrilldownPage />, { wrapper: wrapper() });
    await screen.findByText("Ada");
    const body = document.body.textContent ?? "";
    expect(body).toContain("2/5 exercises");
    expect(body).toContain("in progress"); // underscore humanized
    expect(body).toContain("88 pts");
    expect(body).toContain("—"); // null score
    expect(screen.getByText("Overdue")).toBeTruthy(); // only on the overdue project
    expect(body).toContain("Last active: Never"); // null last_active_at
    // deep links to the skill and project
    expect(screen.getByText("Prompting").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/skills/s-1",
    );
    expect(screen.getByText("Chatbot").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/projects/p-1",
    );
  });

  it("empty assignment sections + null user name fallback", async () => {
    api.mockResolvedValue({ data: { ...DRILL, user_name: null, skills: [], projects: [] } });
    render(<LearnerDrilldownPage />, { wrapper: wrapper() });
    await screen.findByText("Learner"); // name fallback
    expect(screen.getByText("No skills assigned")).toBeTruthy();
    expect(screen.getByText("No projects assigned")).toBeTruthy();
  });

  it("fetch error surfaces a failure line", async () => {
    api.mockRejectedValue(new Error("drill down"));
    render(<LearnerDrilldownPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toMatch(/Failed|error/i));
  });
});
