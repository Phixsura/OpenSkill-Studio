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
const replace = vi.fn();
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/experiments/decisions",
  useRouter: () => ({ replace, push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({ decisionId: "D".repeat(26) }),
}));
vi.mock("@/lib/use-me", () => ({ usePlatformAdmin: () => true }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import DecisionsPage from "@/app/(dashboard)/dashboard/experiments/decisions/page";
import DecisionDetailPage from "@/app/(dashboard)/dashboard/experiments/decisions/[decisionId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const RECORD = {
  id: "D".repeat(26),
  experiment_id: "E".repeat(26),
  decision: "promote",
  summary: "Clear win on exposure, guardrails clean across the window.",
  domain: "learning",
  analysis_type: "randomized",
  analysis_result_hash: "c".repeat(64),
  approver_user_id: "U".repeat(26),
  guardrail_outcome: { clean: true },
  created_at: "2026-10-02T12:00:00Z",
};

beforeEach(() => vi.clearAllMocks());

describe("Decision registry pages (ADR-017 Part L, round 103)", () => {
  it("lists decision records with their verdicts", async () => {
    api.mockImplementation((async (rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path.includes("/decisions/meta"))
        return { data: { total: 1, by_decision: { promote: 1 } } };
      if (path.includes("/experiments/decisions?")) return { data: [RECORD], meta: { total: 1 } };
      return { data: [] };
    }) as never);
    render(<DecisionsPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/Clear win on exposure/)).toBeTruthy();
    expect(screen.getAllByText(/promote/).length).toBeGreaterThanOrEqual(1);
  });

  it("detail renders the summary and the full result hash", async () => {
    api.mockImplementation((async (rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path.endsWith(`/experiments/decisions/${"D".repeat(26)}`)) return { data: RECORD };
      return { data: [] };
    }) as never);
    render(<DecisionDetailPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/Clear win on exposure/)).toBeTruthy();
    expect(screen.getByText("c".repeat(64))).toBeTruthy();
  });
});
