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
vi.mock("next/navigation", () => ({
  useParams: () => ({ experimentId: "E".repeat(26) }),
  usePathname: () => "/dashboard/experiments",
}));
vi.mock("@/lib/use-me", () => ({ usePlatformAdmin: () => true }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ExperimentMetricsPage from "@/app/(dashboard)/dashboard/experiments/[experimentId]/metrics/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function snap(variant: string, day: string, numerator: number, denominator: number, segment = "") {
  return {
    id: `${variant}-${day}`,
    experiment_id: "E".repeat(26),
    metric_key: "exposure_rate",
    variant_key: variant,
    segment,
    window_start: `${day}T00:00:00Z`,
    window_end: `${day}T23:59:59Z`,
    n: denominator,
    numerator,
    denominator,
    sum_value: null,
    sum_sq: null,
    provenance: { source: "exposures", query_version: 1 },
    computed_at: `${day}T23:59:59Z`,
  };
}

beforeEach(() => vi.clearAllMocks());

describe("Metric snapshots page (ADR-017 Part L, round 89 sparkline)", () => {
  it("renders a per-variant trend sparkline over the daily windows", async () => {
    api.mockResolvedValue({
      data: [
        snap("control", "2026-10-01", 10, 40),
        snap("control", "2026-10-02", 12, 40),
        snap("treatment", "2026-10-01", 20, 40),
        snap("treatment", "2026-10-02", 28, 40),
        // segment slices must NOT enter the trend
        snap("treatment", "2026-10-02", 999, 1000, "org:" + "O".repeat(26)),
      ],
    } as never);
    render(<ExperimentMetricsPage />, { wrapper: wrapper() });
    const spark = await screen.findByTestId("metric-sparkline");
    expect(spark.querySelectorAll("polyline").length).toBe(2);
    // legend names both variants
    expect(screen.getAllByText("control").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("treatment").length).toBeGreaterThanOrEqual(1);
  });

  it("skips the sparkline with fewer than two usable points", async () => {
    api.mockResolvedValue({
      data: [snap("control", "2026-10-01", 10, 40)],
    } as never);
    render(<ExperimentMetricsPage />, { wrapper: wrapper() });
    expect(await screen.findByText("exposure_rate")).toBeTruthy();
    expect(screen.queryByTestId("metric-sparkline")).toBeNull();
  });
});
