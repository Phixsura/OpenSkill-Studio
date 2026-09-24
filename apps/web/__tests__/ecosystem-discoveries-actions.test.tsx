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
  usePathname: () => "/dashboard/ecosystem/discoveries",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import DiscoveriesPage from "@/app/(dashboard)/dashboard/ecosystem/discoveries/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function obs(id: string, verified: boolean) {
  return {
    id,
    event_type: "model_release",
    entity_kind: "model",
    external_ref: `ref-${id}`,
    canonical_entity_id: null,
    observed_at: "2026-09-20T00:00:00Z",
    confidence: 0.8,
    extraction_method: "adapter",
    human_verified: verified,
    provenance_url: null,
    normalized: {},
  };
}

beforeEach(() => {
  vi.clearAllMocks();
  api.mockImplementation((path: string, init?: RequestInit) => {
    if (path.startsWith("/ecosystem/observations?") && !init)
      return Promise.resolve({
        data: [obs("O1".padEnd(26, "x"), false), obs("O2".padEnd(26, "x"), true)],
      });
    if (path === "/ecosystem/resolution-candidates" && !init)
      return Promise.resolve({
        data: [
          {
            id: "R1".padEnd(26, "x"),
            entity_kind: "model",
            candidate_entity_id: null,
            match_method: "none",
            confidence: 0,
            status: "pending",
            proposed_payload: { name: "Fresh Model" },
          },
        ],
      });
    return Promise.resolve({ data: {} });
  });
});

describe("Discoveries review actions (ADR-016 §11 UI)", () => {
  it("Verify-all sends ONLY the unverified observation ids", async () => {
    render(<DiscoveriesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText(/Verify all shown \(1\)/));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === "/ecosystem/observations/bulk-verify" && (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    // The already-verified O2 row must NOT be re-sent
    expect(body.ids).toEqual(["O1".padEnd(26, "x")]);
  });

  it("Confirm and Reject hit the specific resolution candidate", async () => {
    render(<DiscoveriesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Confirm"));
    fireEvent.click(screen.getByText("Reject"));
    await new Promise((r) => setTimeout(r, 0));
    const paths = api.mock.calls
      .filter((c) => (c[1] as RequestInit)?.method === "POST")
      .map((c) => c[0]);
    expect(paths).toContain(`/ecosystem/resolution-candidates/${"R1".padEnd(26, "x")}/confirm`);
    expect(paths).toContain(`/ecosystem/resolution-candidates/${"R1".padEnd(26, "x")}/reject`);
  });

  it("LLM suggest is offered only for NEW-entity proposals and POSTs", async () => {
    render(<DiscoveriesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText(/LLM suggest/));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          c[0] === `/ecosystem/resolution-candidates/${"R1".padEnd(26, "x")}/llm-suggest` &&
          (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
  });
});
