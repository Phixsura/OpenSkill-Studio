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

import WorkflowRunsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/workflow-runs/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function run(id: string, status: string, error_code: string | null = null) {
  return { id, status, error_code, created_at: "2026-09-01T10:00:00Z" };
}

beforeEach(() => vi.clearAllMocks());

describe("WorkflowRunsPage (R463)", () => {
  it("renders run rows with status badge, error code, and detail links", async () => {
    api.mockResolvedValue({
      data: [run("run-1", "completed"), run("run-2", "failed", "WF_STEP_ERROR")],
      meta: { total: 2, has_more: false },
    });
    render(<WorkflowRunsPage />, { wrapper: wrapper() });
    await screen.findByText("run-1");
    const body = document.body.textContent ?? "";
    expect(body).toContain("WF_STEP_ERROR"); // error code surfaced on failed run
    expect(screen.getByText("completed")).toBeTruthy();
    expect(screen.getByText("run-1").closest("a")?.getAttribute("href")).toBe(
      "/dashboard/orgs/o-1/workflow-runs/run-1",
    );
    // a terminal-only list does NOT poll (refetchInterval false → one fetch)
    const fetches = api.mock.calls.length;
    await new Promise((r) => setTimeout(r, 50));
    expect(api.mock.calls.length).toBe(fetches);
  });

  it("empty and error states", async () => {
    api.mockResolvedValue({ data: [], meta: { total: 0, has_more: false } });
    const r1 = render(<WorkflowRunsPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/No workflow runs yet/)).toBeTruthy();
    r1.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("runs down"));
    render(<WorkflowRunsPage />, { wrapper: wrapper() });
    await waitFor(() => expect(document.body.textContent).toMatch(/Failed to load workflow runs/));
  });
});
