import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
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

describe("Analysis decision-support extras (v2 round 10)", () => {
  it("renders time-stratified and corpus-shrunk context lines", async () => {
    const payload = analysisPayload();
    const metrics = (
      payload.data as { metrics: Record<string, { comparisons: Record<string, object> }> }
    ).metrics;
    metrics.exposure_rate!.comparisons.treatment = {
      effect: 0.05,
      ci: [0.01, 0.09],
      p: 0.02,
      time_stratified: { effect: 0.048, se: 0.01, ci: [0.03, 0.07], strata: 5 },
      corpus_prior: { n_experiments: 4, mean: 0.02, sd: 0.01 },
      shrunk_effect: 0.031,
    };
    api.mockResolvedValue(payload);
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/Time-stratified: 0\.0480 over 5 windows/)).toBeTruthy();
    expect(
      screen.getByText(/Corpus-shrunk: 0\.0310 \(prior of 4 decided experiments\)/),
    ).toBeTruthy();
  });

  it("renders the new health warnings verbatim", async () => {
    api.mockResolvedValue(
      analysisPayload({
        warnings: ["PRE_BALANCE_SUSPECT", "NOVELTY_EFFECT_DECAY_SUSPECT"],
      }),
    );
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/PRE_BALANCE_SUSPECT/)).toBeTruthy();
    expect(screen.getByText(/NOVELTY_EFFECT_DECAY_SUSPECT/)).toBeTruthy();
  });
});

describe("Bandit suggestion banner", () => {
  it("renders advisory weights and p(best)", async () => {
    api.mockResolvedValue(
      analysisPayload({
        bandit: {
          metric: "exposure_rate",
          p_best: { control: 0.03, treatment: 0.97 },
          suggested_weights_bp: { control: 300, treatment: 9700 },
        },
      }),
    );
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/Bandit suggestion/)).toBeTruthy();
    expect(screen.getByText(/treatment 97\.0%/)).toBeTruthy();
    expect(screen.getByText(/advisory/)).toBeTruthy();
  });
});

describe("Segment picker (v2 §4.8)", () => {
  it("runs the analysis against the chosen segment", async () => {
    api.mockImplementation(async (path: string) => {
      if (String(path).endsWith("/segments")) {
        return { data: ["org:AAAA", "org:BBBB"] };
      }
      return analysisPayload();
    });
    render(<AnalysisPage />, { wrapper: wrapper() });
    const select = (await screen.findByLabelText("Segment")) as HTMLSelectElement;
    fireEvent.change(select, { target: { value: "org:AAAA" } });
    fireEvent.click(screen.getByText("Run analysis"));
    await waitFor(() =>
      expect(
        api.mock.calls.some((c) => String(c[0]).includes("/analysis?segment=org%3AAAAA")),
      ).toBe(true),
    );
  });

  it("hides the picker when no segments exist", async () => {
    api.mockResolvedValue({ data: [] });
    render(<AnalysisPage />, { wrapper: wrapper() });
    await waitFor(() => expect(api).toHaveBeenCalled());
    expect(screen.queryByLabelText("Segment")).toBeNull();
  });
});
