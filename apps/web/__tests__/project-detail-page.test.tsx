import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ orgId: "o-1", projectId: "p-1" }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/components/peer-review-section", () => ({
  PeerReviewSection: () => <div data-testid="peer-review" />,
}));
vi.mock("@/components/media-preview", () => ({
  MediaPreview: () => <div data-testid="media-preview" />,
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ProjectDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/projects/[projectId]/page";
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
  description: "Build one",
  instructions: "Do it",
  status: "published",
  project_type: "general",
  rubric: [{ criterion: "Quality", max_score: 100 }],
  difficulty: "intermediate",
  max_score: 100,
  deadline: null,
  late_deadline: null,
  late_penalty_pct: 10,
  deliverables: [],
};
const SUBS = [
  {
    id: "sub-mine",
    user_id: "u-me",
    version: 2,
    status: "in_review",
    submitted_at: "2026-09-01T00:00:00Z",
    final_score: null,
    author_name: "Me",
  },
  {
    id: "sub-other",
    user_id: "u-other",
    version: 1,
    status: "approved",
    submitted_at: "2026-09-02T00:00:00Z",
    final_score: 88,
    author_name: "Ada",
  },
];

function route(opts: {
  role?: string | null;
  status?: string;
  posts?: { path: string; method: string }[];
}) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      opts.posts?.push({ path, method: init.method });
      return Promise.resolve({ data: { ok: true } });
    }
    if (path === "/orgs/o-1/projects/p-1")
      return Promise.resolve({ data: { ...PROJECT, status: opts.status ?? "published" } });
    if (path.endsWith("/submissions")) return Promise.resolve({ data: SUBS });
    if (path === "/orgs/o-1") return Promise.resolve({ data: { role: opts.role ?? "member" } });
    if (path === "/auth/me") return Promise.resolve({ data: { id: "u-me" } });
    if (path.endsWith("/assets")) return Promise.resolve({ data: [] });
    if (path.endsWith("/creators")) return Promise.resolve({ data: [] });
    if (path.includes("/submissions/sub-mine")) return Promise.resolve({ data: { items: [] } });
    return Promise.resolve({ data: [] });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("ProjectDetailPage (R490)", () => {
  it("instructor on a draft sees Publish + the draft warning; publish POSTs", async () => {
    const posts: { path: string; method: string }[] = [];
    route({ role: "instructor", status: "draft", posts });
    render(<ProjectDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot");
    expect(await screen.findByRole("button", { name: "Publish" })).toBeTruthy();
    expect(screen.getByText(/students cannot see or submit/)).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Unpublish" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Publish" }));
    await waitFor(() =>
      expect(posts.some((p) => p.path === "/orgs/o-1/projects/p-1/publish")).toBe(true),
    );
    await waitFor(() => expect(toasts.success).toHaveBeenCalledWith("Project published"));
  });

  it("instructor on a published project sees Unpublish; plain member sees neither button", async () => {
    route({ role: "admin", status: "published" });
    const first = render(<ProjectDetailPage />, { wrapper: wrapper() });
    await first.findByText("Chatbot");
    expect(await screen.findByRole("button", { name: "Unpublish" })).toBeTruthy();
    // published projects must NOT also offer Publish
    expect(screen.queryByRole("button", { name: "Publish" })).toBeNull();
    first.unmount();

    vi.clearAllMocks();
    route({ role: "member", status: "draft" });
    render(<ProjectDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot");
    expect(screen.queryByRole("button", { name: "Publish" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Unpublish" })).toBeNull();
  });

  it("member heading says My Submissions with no author chips; instructor sees authors", async () => {
    route({ role: "member" });
    const first = render(<ProjectDetailPage />, { wrapper: wrapper() });
    await first.findByText("Chatbot");
    expect(screen.getByText("My Submissions")).toBeTruthy();
    expect(screen.queryByText("Ada")).toBeNull(); // author names are instructor-only
    first.unmount();

    vi.clearAllMocks();
    route({ role: "owner" });
    render(<ProjectDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot");
    expect(screen.getByText("Submissions")).toBeTruthy();
    expect(screen.getByText("Ada")).toBeTruthy();
    // score shown only when final_score present
    expect(screen.getByText("88/100")).toBeTruthy();
    expect(screen.getByText(/v1 —/).closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/projects/p-1/submissions/sub-other",
    );
  });

  it("sidebar hides zero late penalty and null deadline; humanized status", async () => {
    route({ role: "member" });
    render(<ProjectDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Chatbot");
    const body = document.body.textContent ?? "";
    expect(body).toContain("Late Penalty");
    expect(body).toContain("10%");
    expect(body).not.toContain("Deadline"); // null deadline row hidden
    expect(body).toContain("in review"); // status underscores humanized
  });
});
