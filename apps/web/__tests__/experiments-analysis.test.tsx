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
vi.mock("@/lib/use-me", () => ({ usePlatformAdmin: () => true }));
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

  it("renders the multi-covariate CUPED line without the pct field (#61)", async () => {
    // §4.6 v3: the multi shape has NO variance_reduction_pct — the old
    // render called .toFixed on undefined and crashed the whole table
    const payload = analysisPayload();
    const metrics = (
      payload.data as { metrics: Record<string, { comparisons: Record<string, object> }> }
    ).metrics;
    metrics.exposure_rate!.comparisons.treatment = {
      effect: 0.05,
      ci: [0.01, 0.09],
      p: 0.02,
      cuped: {
        effect: 0.042,
        ci: [0.02, 0.064],
        p: 0.01,
        theta: { revision_count: 0.3, project_approval_rate: -0.1 },
        covariates: ["revision_count", "project_approval_rate"],
        mode: "multi",
      },
    };
    api.mockResolvedValue(payload);
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/CUPED ×2: 0\.0420/)).toBeTruthy();
  });

  it("renders the binary-CUPED caveat inline (round 145)", async () => {
    const payload = analysisPayload();
    const metrics = (
      payload.data as { metrics: Record<string, { comparisons: Record<string, object> }> }
    ).metrics;
    metrics.exposure_rate!.comparisons.treatment = {
      effect: 0.05,
      ci: [0.01, 0.09],
      p: 0.02,
      cuped: {
        effect: 0.042,
        ci: [0.02, 0.064],
        p: 0.01,
        theta: 0.3,
        variance_reduction_pct: 22.4,
        caveat: "linear adjustment on a per-unit 0/1 outcome",
      },
    };
    api.mockResolvedValue(payload);
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/linear adjustment on a per-unit 0\/1 outcome/)).toBeTruthy();
  });

  it("renders quantile lines when the comparison carries them (§4.14)", async () => {
    const payload = analysisPayload();
    const metrics = (
      payload.data as { metrics: Record<string, { comparisons: Record<string, object> }> }
    ).metrics;
    metrics.exposure_rate!.comparisons.treatment = {
      effect: 0.05,
      ci: [0.01, 0.09],
      p: 0.02,
      quantiles: {
        "0.5": { control: 101.2, treatment: 304.5, diff: 203.3, ci: [150, 260] },
        "0.95": { control: 900.0, treatment: 850.0, diff: -50.0, ci: [-120, 30] },
      },
    };
    api.mockResolvedValue(payload);
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/p50: 101\.2000 → 304\.5000 \(\+203\.3000\)/)).toBeTruthy();
    expect(screen.getByText(/p95: 900\.0000 → 850\.0000 \(-50\.0000\)/)).toBeTruthy();
  });

  it("renders the look history card when looks exist (round 138)", async () => {
    api.mockImplementation(async (path: string) => {
      if (String(path).endsWith("/analysis/history")) {
        return {
          data: [
            {
              at: "2026-10-02T10:00:00Z",
              sequential: "obrien_fleming",
              look: 2,
              result_hash: "b".repeat(64),
              automated: true,
            },
            {
              at: "2026-10-01T10:00:00Z",
              sequential: "obrien_fleming",
              look: 1,
              result_hash: "a".repeat(64),
              automated: false,
            },
          ],
        };
      }
      return { data: [] };
    });
    render(<AnalysisPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Look history (newest first)")).toBeTruthy();
    expect(screen.getByText(/look 2/)).toBeTruthy();
    expect(screen.getByText(/automated/)).toBeTruthy();
    expect(screen.getByText(/bbbbbbbbbbbb…/)).toBeTruthy();
  });

  it("renders the ITS block for observational runs (round 180)", async () => {
    const payload = analysisPayload();
    const metrics = (payload.data as { metrics: Record<string, object> }).metrics;
    metrics.exposure_rate = {
      ...(metrics.exposure_rate as object),
      its: {
        level_change: { estimate: 4.2, p: 0.003 },
        trend_change: { estimate: 0.9, p: 0.21 },
        n_pre: 14,
        n_post: 14,
        caveat: "interrupted time series — association only",
      },
    };
    api.mockResolvedValue(payload);
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/ITS \(observational\): level 4\.2000/)).toBeTruthy();
    expect(screen.getByText(/14\+14 days/)).toBeTruthy();
    expect(screen.getByText(/association only/)).toBeTruthy();
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
  it("renders the power banner for an underpowered read", async () => {
    api.mockResolvedValue(
      analysisPayload({
        power: {
          metric_key: "exposure_rate",
          baseline_rate: 0.5,
          mde: 0.2,
          required_n_per_arm: 392,
          min_arm_n: 20,
          powered: false,
        },
        warnings: ["SAMPLE_BELOW_POWER_TARGET"],
      }),
    );
    render(<AnalysisPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByText("Run analysis"));
    expect(await screen.findByText(/Underpowered/)).toBeTruthy();
    expect(screen.getByText(/20 \/ 392 units per arm/)).toBeTruthy();
    expect(screen.getByText(/SAMPLE_BELOW_POWER_TARGET/)).toBeTruthy();
  });

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
