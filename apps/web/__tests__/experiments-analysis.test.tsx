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
  usePathname: () => "/dashboard/experiments/x/analysis",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useParams: () => ({ experimentId: "E".repeat(26) }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import AnalysisPage from "@/app/(dashboard)/dashboard/experiments/[experimentId]/analysis/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function analysisPayload(overrides: Record<string, unknown> = {}) {
  return {
    data: {
      engine: "frequentist",
      sequential: "msprt",
      analysis_type: "randomized",
      causal_claim: true,
      control: "control",
      warnings: [],
      result_hash: "a".repeat(64),
      metrics: {
        exposure_rate: {
          role: "primary",
          kind: "rate",
          comparisons: {
            treatment: {
              effect: 0.05,
              relative: 0.5,
              ci: [0.01, 0.09],
              p: 0.02,
              always_valid_p: 0.11,
            },
          },
        },
      },
      ...overrides,
    },
  };
}

beforeEach(() => vi.clearAllMocks());

describe("Analysis view (ADR-017 §10)", () => {
  it("renders effect, CI and always-valid p after running", async () => {
    api.mockResolvedValue(analysisPayload());
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/exposure_rate/)).toBeTruthy();
    expect(screen.getByText("0.0500")).toBeTruthy();
    expect(screen.getByText(/always-valid p 0\.1100/)).toBeTruthy();
    expect(screen.getByText(/result hash/)).toBeTruthy();
  });

  it("shows the no-causal-claim banner for observational analyses", async () => {
    api.mockResolvedValue(
      analysisPayload({
        analysis_type: "observational",
        causal_claim: false,
        caveat: "Observational analysis — associations only.",
      }),
    );
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect((await screen.findByRole("alert")).textContent).toContain(
      "Observational — no causal claim.",
    );
  });

  it("surfaces snapshot-version warnings and OF looks", async () => {
    api.mockResolvedValue(
      analysisPayload({
        sequential: "obrien_fleming",
        looks: { used: 2, max: 4 },
        warnings: ["SNAPSHOT_VERSION_MIXED"],
      }),
    );
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/SNAPSHOT_VERSION_MIXED/)).toBeTruthy();
    expect(screen.getByText("2/4")).toBeTruthy();
  });
});
