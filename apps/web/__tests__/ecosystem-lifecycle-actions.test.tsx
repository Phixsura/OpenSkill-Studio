import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem/components",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ComponentsPage from "@/app/(dashboard)/dashboard/ecosystem/components/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const GOOD = "C1".padEnd(26, "g");
const BAD = "C2".padEnd(26, "b");
const DRAFT = "D1".padEnd(26, "d");
const PLAN = "P1".padEnd(26, "p");

function candidate(id: string, hardCompatible: boolean) {
  return {
    id,
    deprecated_kind: "model_version",
    deprecated_id: "X".repeat(26),
    candidate_id: "Y".repeat(26),
    score: 0.8,
    hard_compatible: hardCompatible,
    hard_failures: hardCompatible ? [] : [{ code: "modality", detail: "text vs image" }],
    explanation: [{ factor: "score", text: "better" }],
    status: "proposed",
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  api.mockImplementation((path: string, init?: RequestInit) => {
    if (path === "/ecosystem/replacements/candidates" && !init)
      return Promise.resolve({ data: [candidate(GOOD, true), candidate(BAD, false)] });
    if (path === "/ecosystem/drafts" && !init)
      return Promise.resolve({
        data: [
          {
            id: DRAFT,
            draft_type: "workflow_pack",
            title: "Migrate pack",
            status: "in_review",
            payload: {},
            validation: { valid: true, errors: [] },
            published_ref: null,
            created_at: "2026-09-20T00:00:00Z",
          },
        ],
      });
    if (path === "/ecosystem/rollouts" && !init)
      return Promise.resolve({
        data: [
          {
            id: PLAN,
            scope_type: "benchmark_only",
            status: "evaluating",
            guardrails: { min_samples: 5 },
            comparison: { sample_size: 10, regressions: [] },
            created_at: "2026-09-20T00:00:00Z",
          },
        ],
      });
    return Promise.resolve({ data: [] });
  });
});

describe("Component lifecycle actions (ADR-016 §21/§22 UI)", () => {
  it("hard-incompatible candidates are never approvable; compatible ones POST the decision", async () => {
    render(<ComponentsPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Replacements"));
    expect(await screen.findByText(/never approvable/)).toBeDefined();
    // Only ONE Approve button (the compatible candidate)
    const approves = screen.getAllByText("Approve");
    expect(approves).toHaveLength(1);
    fireEvent.click(approves[0]!);
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === `/ecosystem/replacements/candidates/${GOOD}/decide` &&
        (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    expect(JSON.parse((call![1] as RequestInit).body as string).decision).toBe("approve");
  });

  it("in-review draft approve POSTs to the draft action endpoint", async () => {
    render(<ComponentsPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Drafts"));
    fireEvent.click(await screen.findByText("Approve"));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          c[0] === `/ecosystem/drafts/${DRAFT}/approve` && (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
  });

  it("evaluating rollout promote POSTs decide with decision=promote", async () => {
    render(<ComponentsPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Rollouts"));
    fireEvent.click(await screen.findByText(/[Pp]romote/));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === `/ecosystem/rollouts/${PLAN}/decide` && (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    expect(JSON.parse((call![1] as RequestInit).body as string).decision).toBe("promote");
  });
});
