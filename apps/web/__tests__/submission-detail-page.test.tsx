import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "o-1", projectId: "p-1", submissionId: "sub-1" }),
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("@/components/annotated-media", () => ({
  AnnotatedImage: () => <div data-testid="annotated-image" />,
}));
vi.mock("@/components/comment-panel", () => ({ CommentPanel: () => <div /> }));
vi.mock("@/components/generation-data", () => ({
  GenerationData: () => <div />,
  parseGenerationMeta: () => null,
}));
vi.mock("@/components/media-preview", () => ({
  MediaPreview: () => <div data-testid="media-preview" />,
}));
vi.mock("@/components/prompt-display", () => ({
  PromptDisplay: () => <div data-testid="prompt-display" />,
}));
vi.mock("@/components/version-compare", () => ({
  VersionCompare: () => <div data-testid="version-compare" />,
}));
vi.mock("@/components/version-history", () => ({
  VersionHistory: () => <div data-testid="version-history" />,
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import SubmissionDetailPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/projects/[projectId]/submissions/[submissionId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function item(over: Partial<Record<string, unknown>> = {}) {
  return {
    id: "it-1",
    deliverable_id: "d-1",
    type: "file",
    file_name: "hero-v1.png",
    mime_type: "image/png",
    content: null,
    version: 1,
    note: null,
    created_at: "2026-09-01T00:00:00Z",
    ...over,
  };
}

function sub(over: Partial<Record<string, unknown>> = {}) {
  return {
    id: "sub-1",
    version: 2,
    status: "submitted",
    submitted_at: "2026-09-01T00:00:00Z",
    is_late: true,
    final_score: null,
    items: [item()],
    reviews: [],
    ...over,
  };
}

function route(theSub: unknown, role = "member") {
  api.mockImplementation(((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path === "/orgs/o-1") return Promise.resolve({ data: { role } });
    if (path.endsWith("/comments")) return Promise.resolve({ data: [] });
    return Promise.resolve({ data: theSub });
  }) as typeof apiWithAuth);
}

beforeEach(() => vi.clearAllMocks());

describe("SubmissionDetailPage (R492)", () => {
  it("groups items per deliverable and shows only the LATEST version, with history controls on multi-version files", async () => {
    route(
      sub({
        items: [
          item({ id: "it-old", version: 1, file_name: "hero-v1.png" }),
          item({ id: "it-new", version: 3, file_name: "hero-v3.png" }),
          item({
            id: "it-other",
            deliverable_id: "d-2",
            type: "text",
            content: "my text",
            file_name: null,
            mime_type: null,
          }),
        ],
      }),
    );
    render(<SubmissionDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Submission v2");
    // latest wins within the deliverable group
    expect(screen.getByText("hero-v3.png")).toBeTruthy();
    expect(screen.queryByText("hero-v1.png")).toBeNull();
    expect(screen.getByText("v3")).toBeTruthy(); // version chip only for v>1
    // multi-version file deliverable exposes history + compare
    expect(screen.getByTestId("version-history")).toBeTruthy();
    expect(screen.getByTestId("version-compare")).toBeTruthy();
    // text deliverable rendered plainly
    expect(screen.getByText("my text")).toBeTruthy();
    // late chip
    expect(screen.getByText("(Late)")).toBeTruthy();
  });

  it("reviewer-type chips: ai/peer/instructor render distinct labels; score shown when graded", async () => {
    route(
      sub({
        final_score: 88,
        reviews: [
          {
            id: "r-1",
            reviewer_type: "ai",
            status: "completed",
            score: 80,
            feedback: "solid",
            created_at: "2026-09-02T00:00:00Z",
          },
          {
            id: "r-2",
            reviewer_type: "peer",
            status: "completed",
            score: null,
            feedback: null,
            created_at: "2026-09-02T00:00:00Z",
          },
          {
            id: "r-3",
            reviewer_type: "instructor",
            status: "in_progress",
            score: null,
            feedback: null,
            created_at: "2026-09-02T00:00:00Z",
          },
        ],
      }),
    );
    render(<SubmissionDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Submission v2");
    expect(screen.getByText(/AI Review/)).toBeTruthy();
    expect(screen.getByText(/Peer Review/)).toBeTruthy();
    expect(screen.getByText(/Instructor Review/)).toBeTruthy();
    expect(screen.getByText("80 pts")).toBeTruthy();
    expect(screen.getByText("88")).toBeTruthy(); // final score headline
    expect(screen.getByText("in progress")).toBeTruthy(); // humanized status
  });

  it("no-review empty state: instructor on a submitted sub gets the Start review link; member gets plain copy", async () => {
    route(sub(), "instructor");
    const first = render(<SubmissionDetailPage />, { wrapper: wrapper() });
    await first.findByText("Submission v2");
    const link = await screen.findByText("Start review →");
    expect(link.closest("a")?.getAttribute("href")).toBe("/dashboard/orgs/o-1/reviews/sub-1");
    first.unmount();

    vi.clearAllMocks();
    route(sub(), "member");
    render(<SubmissionDetailPage />, { wrapper: wrapper() });
    await screen.findByText("Submission v2");
    await waitFor(() => expect(screen.getByText("No reviews yet.")).toBeTruthy());
    expect(screen.queryByText("Start review →")).toBeNull();
  });

  it("instructor empty state requires SUBMITTED status; draft shows plain copy; load error", async () => {
    route(sub({ status: "draft", is_late: false }), "owner");
    const first = render(<SubmissionDetailPage />, { wrapper: wrapper() });
    await first.findByText("Submission v2");
    await waitFor(() => expect(screen.getByText("No reviews yet.")).toBeTruthy());
    expect(screen.queryByText("Start review →")).toBeNull();
    expect(screen.queryByText("(Late)")).toBeNull();
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("down"));
    render(<SubmissionDetailPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toContain("Failed to load submission"));
  });
});
