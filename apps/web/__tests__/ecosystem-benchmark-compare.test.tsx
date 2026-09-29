import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
let searchParams = new URLSearchParams();
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem/benchmarks",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => searchParams,
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

describe("Suite deep link (R350)", () => {
  it("?suite=<id> pre-filters the runs list without a click", async () => {
    searchParams = new URLSearchParams(`suite=${"S".repeat(26)}`);
    try {
      api.mockImplementation(() => Promise.resolve({ data: [] }));
      render(<BenchmarksPage />, { wrapper: wrapper() });
      // the runs list is fetched pre-filtered by the deep-linked suite
      await waitFor(() =>
        expect(
          api.mock.calls.some((c) => String(c[0]).includes(`suite_id=${"S".repeat(26)}`)),
        ).toBe(true),
      );
    } finally {
      searchParams = new URLSearchParams();
    }
  });
});

describe("Suite/run status filters (R381)", () => {
  it("suite and run status dropdowns refetch with ?status= / &status=", async () => {
    render(<BenchmarksPage />, { wrapper: wrapper() });
    fireEvent.change(await screen.findByLabelText("Filter by suite status"), {
      target: { value: "archived" },
    });
    await waitFor(() =>
      expect(
        api.mock.calls.some(
          (c) => String(c[0]) === "/ecosystem/benchmark/suites?limit=50&offset=0&status=archived",
        ),
      ).toBe(true),
    );
    fireEvent.change(await screen.findByLabelText("Filter by run status"), {
      target: { value: "failed" },
    });
    await waitFor(() =>
      expect(
        api.mock.calls.some((c) =>
          String(c[0]).includes("/ecosystem/benchmark/runs?limit=50&offset=0&status=failed"),
        ),
      ).toBe(true),
    );
  });
});

describe("Run list pagination (R388)", () => {
  it("shows count-of-total and Load more fetches offset=50", async () => {
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (String(path).startsWith("/ecosystem/benchmark/runs?") && !init) {
        const offset = Number(new URLSearchParams(String(path).split("?")[1]).get("offset"));
        return Promise.resolve({
          data: Array.from({ length: 50 }, (_, i) =>
            run(`R${String(offset + i).padStart(25, "0")}`, "completed"),
          ),
          meta: { total: 120, limit: 50, offset },
        });
      }
      return Promise.resolve({ data: [] });
    });
    render(<BenchmarksPage />, { wrapper: wrapper() });
    expect(await screen.findByText("50 of 120")).toBeTruthy();
    fireEvent.click(screen.getByText("Load more"));
    await waitFor(() =>
      expect(api.mock.calls.some((c) => String(c[0]).includes("runs?limit=50&offset=50"))).toBe(
        true,
      ),
    );
    expect(await screen.findByText("100 of 120")).toBeTruthy();
  });
});

describe("Status filters are shareable URL state (R393)", () => {
  it("?suite_status=&run_status= seed both filters", async () => {
    searchParams = new URLSearchParams("suite_status=archived&run_status=failed");
    api.mockImplementation(() =>
      Promise.resolve({ data: [], meta: { total: 0, limit: 50, offset: 0 } }),
    );
    render(<BenchmarksPage />, { wrapper: wrapper() });
    await waitFor(() =>
      expect(
        api.mock.calls.some((c) =>
          String(c[0]).includes("/ecosystem/benchmark/suites?limit=50&offset=0&status=archived"),
        ),
      ).toBe(true),
    );
    await waitFor(() =>
      expect(
        api.mock.calls.some((c) => String(c[0]).includes("runs?limit=50&offset=0&status=failed")),
      ).toBe(true),
    );
    searchParams = new URLSearchParams();
  });
});
