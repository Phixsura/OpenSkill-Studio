import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
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
  usePathname: () => "/dashboard/experiments/metrics",
  useRouter: () => ({ replace, push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/use-me", () => ({ usePlatformAdmin: () => true }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import MetricExplorerPage from "@/app/(dashboard)/dashboard/experiments/metrics/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const DEFINITION = {
  id: "M".repeat(26),
  key: "run_latency_ms",
  title: "Workflow run latency (ms)",
  kind: "continuous",
  domain: "workflow",
  source_kind: "service",
  query_version: 1,
  spec: { source: "workflow_runs", measure: "latency_ms", guardrail_aggregate: "sum" },
  privacy_class: "aggregate_only",
  direction: "decrease_good",
  winsorize_pct: 99.9,
  cap_value: null,
  percentile: null,
  created_at: "2026-10-01T00:00:00Z",
  updated_at: "2026-10-01T00:00:00Z",
};

beforeEach(() => vi.clearAllMocks());

describe("Metric Explorer (ADR-017 Part L, round 102 inline edit)", () => {
  it("renders the guardrail aggregate in the spec column (round 168)", async () => {
    api.mockImplementation(async () => ({ data: [DEFINITION] }));
    render(<MetricExplorerPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/guards sum/)).toBeTruthy();
  });

  it("edits the operational knobs through the PATCH", async () => {
    api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
      const path = String(rawPath ?? "");
      if (init?.method === "PATCH")
        return Promise.resolve({ data: { ...DEFINITION, winsorize_pct: 95 } });
      return Promise.resolve({ data: [DEFINITION] });
    }) as never);
    render(<MetricExplorerPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Edit"));
    fireEvent.change(screen.getByLabelText("winsorize run_latency_ms"), {
      target: { value: "95" },
    });
    fireEvent.change(screen.getByLabelText("cap run_latency_ms"), {
      target: { value: "60000" },
    });
    fireEvent.change(screen.getByLabelText("direction run_latency_ms"), {
      target: { value: "decrease_good" },
    });
    fireEvent.change(screen.getByLabelText("quantiles run_latency_ms"), {
      target: { value: "0.5, 0.95" },
    });
    fireEvent.click(screen.getByText("Save"));
    await vi.waitFor(() => {
      const call = api.mock.calls.find((c) => c[1]?.method === "PATCH");
      expect(call).toBeTruthy();
      const body = JSON.parse(String(call?.[1]?.body));
      expect(body).toEqual({
        direction: "decrease_good",
        winsorize_pct: 95,
        cap_value: 60000,
        quantiles: [0.5, 0.95],
      });
    });
  });

  it("blank winsorize/cap send the explicit clear flags", async () => {
    api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
      if (init?.method === "PATCH") return Promise.resolve({ data: DEFINITION });
      return Promise.resolve({ data: [DEFINITION] });
    }) as never);
    render(<MetricExplorerPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Edit"));
    fireEvent.change(screen.getByLabelText("winsorize run_latency_ms"), {
      target: { value: "" },
    });
    fireEvent.click(screen.getByText("Save"));
    await vi.waitFor(() => {
      const call = api.mock.calls.find((c) => c[1]?.method === "PATCH");
      const body = JSON.parse(String(call?.[1]?.body));
      expect(body.clear_winsorize).toBe(true);
      expect(body.clear_cap).toBe(true);
      expect(body.clear_quantiles).toBe(true);
      // continuous kind: never sends the km knob
      expect("km" in body).toBe(false);
    });
  });

  it("time_to_event rows get the KM toggle; the PATCH carries it (round 186)", async () => {
    const tte = {
      ...DEFINITION,
      key: "placement_outcome_rate",
      title: "Placement outcome",
      kind: "time_to_event",
      spec: { source: "talent_outcomes", km: true },
      winsorize_pct: null,
    };
    api.mockImplementation(((rawPath: unknown, init?: { method?: string; body?: string }) => {
      if (init?.method === "PATCH") return Promise.resolve({ data: tte });
      return Promise.resolve({ data: [tte] });
    }) as never);
    render(<MetricExplorerPage />, { wrapper: wrapper() });
    // the spec column badges the opted-in definition
    expect(await screen.findByText(/· KM/)).toBeTruthy();
    fireEvent.click(screen.getByText("Edit"));
    const toggle = screen.getByLabelText("km placement_outcome_rate") as HTMLInputElement;
    expect(toggle.checked).toBe(true); // initialized from spec.km
    fireEvent.click(toggle); // switch it OFF
    fireEvent.click(screen.getByText("Save"));
    await vi.waitFor(() => {
      const call = api.mock.calls.find((c) => c[1]?.method === "PATCH");
      const body = JSON.parse(String(call?.[1]?.body));
      expect(body.km).toBe(false);
    });
  });

  it("billing time_to_event rows get NO KM toggle (round 189, #70)", async () => {
    const billing = {
      ...DEFINITION,
      key: "retention_rate",
      title: "Retention",
      kind: "time_to_event",
      spec: { source: "billing" },
      winsorize_pct: null,
    };
    api.mockImplementation((async () => ({ data: [billing] })) as never);
    render(<MetricExplorerPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Edit"));
    // right kind, wrong source: the reader is placement-based, so the
    // console never offers the knob the API would 422
    expect(screen.queryByLabelText("km retention_rate")).toBeNull();
    fireEvent.click(screen.getByText("Save"));
    await vi.waitFor(() => {
      const call = api.mock.calls.find((c) => c[1]?.method === "PATCH");
      const body = JSON.parse(String(call?.[1]?.body));
      expect("km" in body).toBe(false);
    });
  });
});
