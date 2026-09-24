import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({ usePathname: () => "/dashboard/ecosystem" }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import BenchmarksPage from "@/app/(dashboard)/dashboard/ecosystem/benchmarks/page";
import EcosystemOverviewPage from "@/app/(dashboard)/dashboard/ecosystem/page";
import SourcesPage from "@/app/(dashboard)/dashboard/ecosystem/sources/page";
import ComponentsPage from "@/app/(dashboard)/dashboard/ecosystem/components/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const OVERVIEW = {
  sources: { active: 3, paused: 1, error: 0 },
  discoveries_7d: 12,
  changes_unacknowledged: 4,
  security_critical_open: 1,
  pricing_unreviewed: 2,
  resolution_pending: 5,
  benchmark_queue: 0,
  impact_open: 2,
  replacements_proposed: 1,
  drafts_in_review: 1,
  rollouts_active: 1,
};

beforeEach(() => vi.clearAllMocks());

describe("Ecosystem Intelligence pages (issue #35 Part S)", () => {
  it("overview renders operator health stats and change feed", async () => {
    api.mockImplementation((path: string) => {
      if (path === "/ecosystem/dashboard") return Promise.resolve({ data: OVERVIEW });
      return Promise.resolve({
        data: [
          {
            id: "c1",
            change_type: "price",
            field: "pricing",
            severity: "update_available",
            entity_kind: "model",
            detected_at: "2026-09-20T00:00:00Z",
            acknowledged: false,
          },
        ],
      });
    });
    render(<EcosystemOverviewPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Discoveries (7d)")).toBeTruthy();
    expect(screen.getByText("12")).toBeTruthy();
    expect(screen.getByText("Security critical open")).toBeTruthy();
    expect(await screen.findByText("update available")).toBeTruthy();
  });

  it("sources page lists sources with status and sync action", async () => {
    api.mockResolvedValue({
      data: [
        {
          id: "s1",
          name: "Vendor Catalog",
          source_type: "provider_api",
          trust_level: "official",
          base_url: "https://example.com/models",
          adapter_key: "json_catalog",
          status: "active",
          last_success_at: "2026-09-20T00:00:00Z",
          consecutive_failures: 0,
          robots_compliant: true,
        },
      ],
    });
    render(<SourcesPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Vendor Catalog")).toBeTruthy();
    expect(screen.getByText("Sync now")).toBeTruthy();
    expect(screen.getByText("official")).toBeTruthy();
  });

  it("components page separates hard-incompatible replacements from approvable ones", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/replacements/candidates")) {
        return Promise.resolve({
          data: [
            {
              id: "r1",
              deprecated_kind: "model_version",
              deprecated_id: "A".repeat(26),
              candidate_id: "B".repeat(26),
              score: 0.81,
              hard_compatible: true,
              hard_failures: [],
              explanation: [{ factor: "cost", text: "Cost score 0.72 (vs incumbent)" }],
              status: "proposed",
            },
            {
              id: "r2",
              deprecated_kind: "model_version",
              deprecated_id: "A".repeat(26),
              candidate_id: "C".repeat(26),
              score: 0,
              hard_compatible: false,
              hard_failures: [{ code: "IO_TYPE_MISMATCH", detail: "outputs missing" }],
              explanation: [],
              status: "proposed",
            },
          ],
        });
      }
      return Promise.resolve({ data: [] });
    });
    const { container } = render(<ComponentsPage />, { wrapper: wrapper() });
    // switch to Replacements tab
    const tab = await screen.findByText("Replacements");
    tab.click();
    expect(await screen.findByText(/hard incompatible — never approvable/)).toBeTruthy();
    expect(screen.getByText(/IO_TYPE_MISMATCH/)).toBeTruthy();
    // Only the compatible candidate offers Approve
    const approveButtons = Array.from(container.querySelectorAll("button")).filter(
      (b) => b.textContent === "Approve",
    );
    expect(approveButtons.length).toBe(1);
  });
});

describe("Ecosystem round-5 surfaces", () => {
  it("benchmark leaderboard renders ranked rows with CI and Elo", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/benchmark/leaderboard")) {
        return Promise.resolve({
          data: {
            rows: [
              {
                entity_kind: "model_version",
                entity_id: "A".repeat(26),
                canonical_name: "VisionGen 2.0",
                run_id: "r1",
                finished_at: null,
                total_cost_usd: 0.1,
                dimension_scores: { reliability: 1, human_pref_elo: 1042 },
                dimension_stats: {
                  reliability: { mean: 1, n: 6, ci95: [1, 1] },
                  cost_usd: { mean: 0.03, n: 6, ci95: [0.028, 0.032] },
                  latency_ms: { mean: 800, n: 6, ci95: [750, 850] },
                },
              },
            ],
          },
        });
      }
      return Promise.resolve({ data: [] });
    });
    render(<BenchmarksPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Leaderboard")).toBeTruthy();
    expect(await screen.findByText("VisionGen 2.0")).toBeTruthy();
    expect(screen.getByText("1042")).toBeTruthy(); // Elo column
    expect(screen.getByText(/\u00b10.002/)).toBeTruthy(); // CI half-width on cost
  });

  it("global search box surfaces cross-kind hits", async () => {
    api.mockImplementation((path: string) => {
      if (path === "/ecosystem/dashboard") return Promise.resolve({ data: OVERVIEW });
      if (path.startsWith("/ecosystem/search")) {
        return Promise.resolve({
          data: [
            {
              kind: "model",
              id: "M".repeat(26),
              canonical_name: "Searchable Gen",
              lifecycle_status: "verified",
              score: 0.91,
            },
          ],
        });
      }
      return Promise.resolve({ data: [] });
    });
    render(<EcosystemOverviewPage />, { wrapper: wrapper() });
    const input = await screen.findByLabelText("Search catalog");
    const { fireEvent } = await import("@testing-library/react");
    fireEvent.change(input, { target: { value: "searchable" } });
    fireEvent.submit(input.closest("form")!);
    expect(await screen.findByText("Searchable Gen")).toBeTruthy();
    expect(screen.getByText(/model \u00b7 verified/)).toBeTruthy();
  });
});

describe("fmtDate (ecosystem lib)", () => {
  it("renders valid dates, dashes empties, and passes garbage through verbatim", async () => {
    const { fmtDate } = await import("@/app/(dashboard)/dashboard/ecosystem/lib");
    expect(fmtDate(null)).toBe("—");
    expect(fmtDate(undefined)).toBe("—");
    expect(fmtDate("")).toBe("—");
    expect(fmtDate("not-a-date")).toBe("not-a-date"); // never "Invalid Date"
    expect(fmtDate("2026-09-20T00:00:00Z")).not.toContain("Invalid");
  });
});
