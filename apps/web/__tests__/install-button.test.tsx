import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn(), info: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
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

import { InstallButton } from "@/components/install-button";
import { apiWithAuth, ApiError } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function route(opts: {
  orgs?: unknown[];
  install?: Error | null;
  posts?: { path: string; body: unknown }[];
}) {
  api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
    const path = String(rawPath ?? "");
    if (init?.method === "POST") {
      opts.posts?.push({ path, body: JSON.parse(init.body ?? "{}") });
      if (opts.install instanceof Error) return Promise.reject(opts.install);
      return Promise.resolve({ data: { id: "in-1" } });
    }
    return Promise.resolve({
      data: opts.orgs ?? [{ id: "org-a", name: "Org A", role: "instructor" }],
    });
  }) as typeof apiWithAuth);
}

const props = {
  productType: "workflow_pack" as const,
  packId: "wp-1",
  packName: "Render Pack",
  isAuthed: true,
};

beforeEach(() => vi.clearAllMocks());

describe("InstallButton (R503)", () => {
  it("install posts pack_id to the product-typed endpoint after a two-step confirm; success shows Installed", async () => {
    const posts: { path: string; body: unknown }[] = [];
    route({ posts });
    render(<InstallButton {...props} />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: /Install Render Pack/ }));
    expect(posts.length).toBe(0); // arming does not post
    fireEvent.click(screen.getByRole("button", { name: "Confirm install" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/org-a/workflow-installations");
    expect(posts[0]?.body).toEqual({ pack_id: "wp-1" });
    expect(await screen.findByText("✓ Installed")).toBeTruthy();
  });

  it("skill packs hit /installations, not /workflow-installations", async () => {
    const posts: { path: string; body: unknown }[] = [];
    route({ posts });
    render(<InstallButton {...props} productType="skill_pack" />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: /Install Render Pack/ }));
    fireEvent.click(screen.getByRole("button", { name: "Confirm install" }));
    await waitFor(() => expect(posts.length).toBe(1));
    expect(posts[0]?.path).toBe("/orgs/org-a/installations");
  });

  it("role gate: learner-only orgs get the instructor/admin notice, no install CTA", async () => {
    route({ orgs: [{ id: "org-a", name: "Org A", role: "member" }] });
    render(<InstallButton {...props} />, { wrapper: wrapper() });
    // the no-org notice also renders while the orgs query is loading — wait
    // for the query to SETTLE before asserting, so a dropped role filter
    // (which would then surface the CTA) actually fails this test
    await waitFor(() => expect(api).toHaveBeenCalled());
    await new Promise((r) => setTimeout(r, 20));
    expect(screen.queryByRole("button", { name: /Install Render Pack/ })).toBeNull();
    expect(screen.getByText(/Installing requires an instructor or admin role/)).toBeTruthy();
  });

  it("unauthenticated renders a login link; LICENSE_REQUIRED explains the org mismatch (R113[L8])", async () => {
    route({});
    const first = render(<InstallButton {...props} isAuthed={false} />, { wrapper: wrapper() });
    expect(first.getByText("Sign in to install →").closest("a")?.getAttribute("href")).toBe(
      "/login",
    );
    first.unmount();

    vi.clearAllMocks();
    route({ install: new ApiError(402, "LICENSE_REQUIRED", "license required") });
    render(<InstallButton {...props} />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: /Install Render Pack/ }));
    fireEvent.click(screen.getByRole("button", { name: "Confirm install" }));
    await waitFor(() =>
      expect(toasts.error).toHaveBeenCalledWith(
        expect.stringContaining("license is required for the selected organization"),
      ),
    );
    // still recoverable — the CTA returns instead of a dead Installed state
    expect(await screen.findByRole("button", { name: /Install Render Pack/ })).toBeTruthy();
  });

  it("ALREADY_INSTALLED settles into the Installed badge instead of an error", async () => {
    route({ install: new ApiError(409, "ALREADY_INSTALLED", "dup") });
    render(<InstallButton {...props} />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: /Install Render Pack/ }));
    fireEvent.click(screen.getByRole("button", { name: "Confirm install" }));
    expect(await screen.findByText("✓ Installed")).toBeTruthy();
    expect(toasts.info).toHaveBeenCalled();
    expect(toasts.error).not.toHaveBeenCalled();
  });
});
