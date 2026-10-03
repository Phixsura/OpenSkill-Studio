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
  spec: { source: "workflow_runs", measure: "latency_ms" },
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
    fireEvent.click(screen.getByText("Save"));
    await vi.waitFor(() => {
      const call = api.mock.calls.find((c) => c[1]?.method === "PATCH");
      expect(call).toBeTruthy();
      const body = JSON.parse(String(call?.[1]?.body));
      expect(body).toEqual({
        direction: "decrease_good",
        winsorize_pct: 95,
        cap_value: 60000,
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
    });
  });
});
