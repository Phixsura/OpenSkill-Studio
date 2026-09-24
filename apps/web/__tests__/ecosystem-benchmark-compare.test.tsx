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
  usePathname: () => "/dashboard/ecosystem/benchmarks",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import BenchmarksPage from "@/app/(dashboard)/dashboard/ecosystem/benchmarks/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function run(id: string, status: string) {
  return {
    id,
    error: null,
    suite_id: "SUITE00000000000000000000X",
    status,
    target: { entity_kind: "model_version", entity_id: "M".repeat(26) },
    total_cost_usd: 0.01,
    dimension_scores: { reliability: 0.9 },
    created_at: "2026-09-20T00:00:00Z",
  };
}

const DONE1 = "R1".padEnd(26, "a");
const DONE2 = "R2".padEnd(26, "b");
const RUNNING = "R3".padEnd(26, "c");

beforeEach(() => {
  vi.clearAllMocks();
  api.mockImplementation((path: string, init?: RequestInit) => {
    if (path.startsWith("/ecosystem/benchmark/runs?") && !init)
      return Promise.resolve({
        data: [run(DONE1, "completed"), run(DONE2, "completed"), run(RUNNING, "running")],
      });
    if (path.startsWith("/ecosystem/benchmark/runs/compare"))
      return Promise.resolve({ data: { runs: [], dimensions: [] } });
    return Promise.resolve({ data: [] });
  });
});

describe("Benchmark comparison wiring (ADR-016 §16 UI)", () => {
  it("compare stays disabled under two selections and a running run is unselectable", async () => {
    render(<BenchmarksPage />, { wrapper: wrapper() });
    const boxes = (await screen.findAllByLabelText(
      "Select run for comparison",
    )) as HTMLInputElement[];
    expect(boxes).toHaveLength(3);
    expect(boxes[2]!.disabled).toBe(true); // running run not comparable
    const button = screen.getByText(/Compare selected/) as HTMLButtonElement;
    fireEvent.click(boxes[0]!);
    expect(button.disabled).toBe(true); // 1 selected — still disabled
    fireEvent.click(boxes[1]!);
    expect(button.disabled).toBe(false);
  });

  it("Compare GETs /runs/compare with exactly the selected ids", async () => {
    render(<BenchmarksPage />, { wrapper: wrapper() });
    const boxes = (await screen.findAllByLabelText(
      "Select run for comparison",
    )) as HTMLInputElement[];
    fireEvent.click(boxes[0]!);
    fireEvent.click(boxes[1]!);
    fireEvent.click(screen.getByText(/Compare selected/));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) => typeof c[0] === "string" && (c[0] as string).includes("/runs/compare"),
    );
    expect(call).toBeDefined();
    expect(call![0]).toBe(`/ecosystem/benchmark/runs/compare?ids=${DONE1},${DONE2}`);
  });
});
