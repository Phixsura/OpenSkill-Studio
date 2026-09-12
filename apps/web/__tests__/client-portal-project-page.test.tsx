import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const nav = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock("next/navigation", () => ({
  useParams: () => ({ projectId: "p-1" }),
  useRouter: () => ({ replace: nav.replace }),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/components/status-badge", () => ({
  StatusBadge: ({ status }: { status: string }) => <span>{status}</span>,
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
  return { ApiError: MockApiError };
});
const portal = vi.hoisted(() => ({
  api: vi.fn(),
  role: "commenter" as string,
  token: "guest-jwt" as string | null,
}));
vi.mock("@/lib/client-portal", () => ({
  portalApi: (...args: unknown[]) => portal.api(...args),
  portalRole: () => portal.role,
  portalToken: () => portal.token,
}));

import ClientProjectPage from "@/app/client/[projectId]/page";
import { ApiError } from "@/lib/api";

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const BRIEF = {
  title: "Ad Campaign",
  client_name: "Acme",
  objective: "Sell more",
  target_audience: "Gen Z",
  deliverable_specs: null,
  tone_and_style: "Bold",
  timeline: null,
  evaluation_criteria: null,
};
const SUBMISSION = {
  id: "sub-1",
  version: 2,
  status: "SHARED",
  submitted_at: "2026-09-01T00:00:00Z",
  share_note: "please review",
  items: [
    {
      id: "it-1",
      type: "file",
      file_name: "hero.png",
      mime_type: "image/png",
      content: null,
      version: 1,
    },
  ],
};

function route(opts?: { history?: unknown[]; posts?: { path: string; body?: unknown }[] }) {
  portal.api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      opts?.posts?.push({ path, body: init.body ? JSON.parse(init.body) : undefined });
      return Promise.resolve({ data: { ok: true } });
    }
    if (path.endsWith("/brief")) return Promise.resolve({ data: BRIEF });
    if (path.endsWith("/submissions")) return Promise.resolve({ data: [SUBMISSION] });
    if (path.endsWith("/approval-history")) return Promise.resolve({ data: opts?.history ?? [] });
    if (path.endsWith("/comments")) return Promise.resolve({ data: [] });
    return Promise.resolve({ data: [] });
  }) as typeof portal.api);
}

beforeEach(() => {
  vi.clearAllMocks();
  sessionStorage.clear();
  portal.role = "commenter";
  portal.token = "guest-jwt";
});

describe("ClientProjectPage (R482)", () => {
  it("401 with a guest JWT bounces to /client/access ONCE even when the 401s arrive in two waves (R123 latch)", async () => {
    sessionStorage.setItem("client_portal_jwt", "guest");
    // two-wave arrival: brief 401s immediately; submissions 401s later, AFTER
    // the first classification already swept the guest JWT. Without the latch
    // the second wave misreads the session as member-based and bounces to /login.
    portal.api.mockImplementation(((rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path.endsWith("/brief")) return Promise.reject(new ApiError(401, "EXPIRED", "expired"));
      if (path.endsWith("/submissions"))
        return new Promise((_, reject) =>
          setTimeout(() => reject(new ApiError(401, "EXPIRED", "expired")), 40),
        );
      return Promise.resolve({ data: [] });
    }) as typeof portal.api);
    render(<ClientProjectPage />, { wrapper: wrapper() });
    await waitFor(() => expect(nav.replace).toHaveBeenCalledWith("/client/access"));
    expect(sessionStorage.getItem("client_portal_jwt")).toBeNull(); // JWT swept
    // give the second wave time to land, then assert the latch held
    await new Promise((r) => setTimeout(r, 120));
    expect(nav.replace).not.toHaveBeenCalledWith(expect.stringContaining("/login"));
    expect(nav.replace).toHaveBeenCalledTimes(1);
  });

  it("401 WITHOUT a guest JWT (member session) bounces to /login with a redirect back (R113[H3])", async () => {
    portal.api.mockRejectedValue(new ApiError(401, "EXPIRED", "expired"));
    render(<ClientProjectPage />, { wrapper: wrapper() });
    await waitFor(() =>
      expect(nav.replace).toHaveBeenCalledWith("/login?redirect=%2Fclient%2Fp-1"),
    );
    expect(nav.replace).not.toHaveBeenCalledWith("/client/access");
  });

  it("commenter sees Request revision but NOT approve/final-accept; approver sees all", async () => {
    route();
    const first = render(<ClientProjectPage />, { wrapper: wrapper() });
    await first.findByText("Version 2");
    expect(screen.getByRole("button", { name: "Request revision" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Approve version" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Final accept" })).toBeNull();
    first.unmount();

    vi.clearAllMocks();
    portal.role = "approver";
    route();
    render(<ClientProjectPage />, { wrapper: wrapper() });
    await screen.findByText("Version 2");
    expect(screen.getByRole("button", { name: "Approve version" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Final accept" })).toBeTruthy();
  });

  it("final accept fires only after window.confirm; declined confirm posts nothing (R185)", async () => {
    portal.role = "approver";
    const posts: { path: string; body?: unknown }[] = [];
    route({ posts });
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(false);
    render(<ClientProjectPage />, { wrapper: wrapper() });
    await screen.findByText("Version 2");
    fireEvent.click(screen.getByRole("button", { name: "Final accept" }));
    expect(confirmSpy).toHaveBeenCalled();
    expect(posts.length).toBe(0);
    confirmSpy.mockReturnValue(true);
    fireEvent.click(screen.getByRole("button", { name: "Final accept" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/client-portal/projects/p-1/final-accept");
    expect(posts[0]?.body).toEqual({ submission_id: "sub-1" });
    confirmSpy.mockRestore();
  });

  it("final-accepted history hides all action buttons and shows the banner", async () => {
    route({
      history: [
        {
          id: "h-1",
          action: "final_accepted",
          version: 2,
          comment: null,
          acted_by: "Client X",
          created_at: "2026-09-05T00:00:00Z",
        },
      ],
    });
    portal.role = "approver";
    render(<ClientProjectPage />, { wrapper: wrapper() });
    await screen.findByText("Version 2");
    expect(screen.getByText(/finally accepted/)).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Request revision" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Final accept" })).toBeNull();
    // decision history renders humanized action + actor label
    expect(document.body.textContent).toContain("final accepted");
    expect(document.body.textContent).toContain("Client X");
  });

  it("revision request posts the typed comment; reopening clears stale text (R101[L0])", async () => {
    const posts: { path: string; body?: unknown }[] = [];
    route({ posts });
    render(<ClientProjectPage />, { wrapper: wrapper() });
    await screen.findByText("Version 2");
    fireEvent.click(screen.getByRole("button", { name: "Request revision" }));
    const ta = screen.getByPlaceholderText("What should change?");
    fireEvent.change(ta, { target: { value: "Make it pop" } });
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    // reopen — the typed comment must NOT survive into a fresh card
    fireEvent.click(screen.getByRole("button", { name: "Request revision" }));
    expect((screen.getByPlaceholderText("What should change?") as HTMLTextAreaElement).value).toBe(
      "",
    );
    fireEvent.change(screen.getByPlaceholderText("What should change?"), {
      target: { value: "Bigger logo" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send request" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/client-portal/projects/p-1/submissions/sub-1/request-revision");
    expect(posts[0]?.body).toEqual({ comment: "Bigger logo" });
    await waitFor(() => expect(toasts.success).toHaveBeenCalled());
  });
});
