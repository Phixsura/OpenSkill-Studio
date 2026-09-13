import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children, ...rest }: { href: string; children: ReactNode }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));
vi.mock("@/stores/auth", () => ({
  useAuthStore: (sel: (s: { user: { display_name: string } }) => unknown) =>
    sel({ user: { display_name: "Hana" } }),
}));

import DashboardPage from "@/app/(dashboard)/dashboard/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const OVERVIEW = {
  drafts: [{ submission_id: "s-1", project_id: "p-1", org_id: "o-1", project_title: "Chatbot" }],
  peer_assessments_pending: 2,
  reviews_received: [
    {
      review_id: "r-1",
      score: 88,
      created_at: "2026-09-01T00:00:00Z",
      project_id: "p-1",
      org_id: "o-1",
      submission_id: "s-1",
      project_title: "Chatbot",
    },
    {
      review_id: "r-2",
      score: null,
      created_at: "2026-09-02T00:00:00Z",
      project_id: "p-2",
      org_id: "o-1",
      submission_id: "s-2",
      project_title: "Pipeline",
    },
  ],
  pending_reviews_to_grade: 1,
};

function route(ov: Record<string, unknown> | null, orgs: unknown[] = []) {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path === "/orgs") return Promise.resolve({ data: orgs });
    if (path === "/me/overview") return Promise.resolve({ data: ov });
    return Promise.resolve({ data: null });
  });
}

beforeEach(() => vi.clearAllMocks());

describe("DashboardPage (R417)", () => {
  it("to-dos render counts with singular/plural, drafts deep-link to the submit page", async () => {
    route(OVERVIEW, [{ id: "o-1", name: "Org A", role: "student", member_count: 1 }]);
    render(<DashboardPage />, { wrapper: wrapper() });
    await screen.findByText("To do");
    const body = document.body.textContent ?? "";
    expect(body).toContain("1 submission waiting for your review"); // singular
    expect(body).toContain("2 peer reviews assigned to you"); // plural
    const chatbotLinks = screen
      .getAllByText("Chatbot")
      .map((el) => el.closest("a")?.getAttribute("href"));
    expect(chatbotLinks).toContain("/dashboard/orgs/o-1/projects/p-1/submit");
    expect(chatbotLinks).toContain("/dashboard/orgs/o-1/projects/p-1/submissions/s-1");
    // feedback: scored review shows pts, null score shows none
    expect(body).toContain("88 pts");
    const pipelineRow = screen.getByText("Pipeline").closest("a");
    expect(pipelineRow?.textContent).not.toContain("pts");
    expect(pipelineRow?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/projects/p-2/submissions/s-2",
    );
  });

  it("pending grading ALONE still surfaces the To do section (each arm counts)", async () => {
    route({
      drafts: [],
      peer_assessments_pending: 0,
      reviews_received: [],
      pending_reviews_to_grade: 3,
    });
    render(<DashboardPage />, { wrapper: wrapper() });
    expect(await screen.findByText("To do")).toBeTruthy();
    expect(document.body.textContent ?? "").toContain("3 submissions waiting for your review");
  });

  it("no to-dos → the section is absent entirely; empty orgs shows the create CTA", async () => {
    route({
      drafts: [],
      peer_assessments_pending: 0,
      reviews_received: [],
      pending_reviews_to_grade: 0,
    });
    render(<DashboardPage />, { wrapper: wrapper() });
    await screen.findByText(/Welcome, Hana/);
    expect(screen.queryByText("To do")).toBeNull();
    expect(screen.queryByText("Recent feedback")).toBeNull();
    expect(await screen.findByText(/haven't joined any organizations/)).toBeTruthy();
    expect(screen.getByText("Create your first organization")).toBeTruthy();
  });

  it("org cards render role chip + member pluralization and link to the org", async () => {
    route(
      {
        drafts: [],
        peer_assessments_pending: 0,
        reviews_received: [],
        pending_reviews_to_grade: 0,
      },
      [
        { id: "o-1", name: "Solo Org", role: "owner", member_count: 1 },
        { id: "o-2", name: "Team Org", role: "instructor", member_count: 5 },
      ],
    );
    render(<DashboardPage />, { wrapper: wrapper() });
    await screen.findByText("Solo Org");
    const body = document.body.textContent ?? "";
    expect(body).toContain("1 member");
    expect(body).not.toContain("1 members");
    expect(body).toContain("5 members");
    expect(screen.getByText("Team Org").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-2",
    );
  });
});
