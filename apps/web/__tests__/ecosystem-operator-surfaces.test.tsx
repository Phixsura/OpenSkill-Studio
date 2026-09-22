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
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ComponentsPage from "@/app/(dashboard)/dashboard/ecosystem/components/page";
import EcosystemOverviewPage from "@/app/(dashboard)/dashboard/ecosystem/page";
import SourcesPage from "@/app/(dashboard)/dashboard/ecosystem/sources/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => {
  vi.clearAllMocks();
  api.mockResolvedValue({ data: [], meta: { total: 0 } });
});

describe("Operator surfaces (ADR-016 §52)", () => {
  it("source History panel shows sync runs with errors", async () => {
    api.mockImplementation((path: string) => {
      if (path === "/ecosystem/sources")
        return Promise.resolve({
          data: [
            {
              id: "S".repeat(26),
              name: "HF feed",
              source_type: "registry",
              trust_level: "official",
              base_url: "https://x",
              adapter_key: "huggingface",
              status: "active",
              last_success_at: null,
              consecutive_failures: 2,
              robots_compliant: true,
            },
          ],
        });
      if (path.includes("/sync-runs"))
        return Promise.resolve({
          data: [
            {
              id: "r1",
              status: "failed",
              http_status: 502,
              bytes_fetched: 0,
              observations_created: 0,
              changes_detected: 0,
              error: "ECO_FETCH_FAILED: upstream 502",
              started_at: "2026-09-22T10:00:00Z",
              finished_at: "2026-09-22T10:00:05Z",
            },
          ],
        });
      return Promise.resolve({ data: [] });
    });
    render(<SourcesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("History"));
    expect(await screen.findByText("Sync history (last 20)")).toBeDefined();
    expect(await screen.findByText(/ECO_FETCH_FAILED/)).toBeDefined();
    expect(screen.getByText("502")).toBeDefined();
  });

  it("impact analyses expose acknowledge/resolve actions", async () => {
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (path === "/ecosystem/impact/analyses" && !init)
        return Promise.resolve({
          data: [
            {
              id: "ia1",
              root_kind: "model_version",
              root_id: "0".repeat(26),
              classification: "sunset",
              status: "open",
              summary: { workflows: 3 },
              deadline_at: "2026-10-01T00:00:00Z",
              computed_at: "2026-09-20T00:00:00Z",
            },
          ],
        });
      return Promise.resolve({ data: [] });
    });
    render(<ComponentsPage />, { wrapper: wrapper() });
    expect(await screen.findByText("Acknowledge")).toBeDefined();
    fireEvent.click(screen.getByText("Acknowledge"));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) =>
          typeof c[0] === "string" &&
          c[0].includes("/impact/analyses/ia1/status?status=acknowledged") &&
          (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
  });

  it("overview stat cards link to their work queues", async () => {
    api.mockImplementation((path: string) => {
      if (path === "/ecosystem/dashboard")
        return Promise.resolve({
          data: {
            sources: { active: 1, paused: 0, error: 0 },
            sources_stale: 0,
            discoveries_7d: 2,
            observations_unverified: 0,
            injection_flagged_unverified: 0,
            changes_unacknowledged: 0,
            security_critical_open: 0,
            security_advisories_open: 0,
            pricing_unreviewed: 4,
            resolution_pending: 0,
            benchmark_queue: 0,
            impact_open: 0,
            replacements_proposed: 0,
            drafts_in_review: 0,
            rollouts_active: 0,
          },
        });
      return Promise.resolve({ data: [] });
    });
    render(<EcosystemOverviewPage />, { wrapper: wrapper() });
    const pricingCard = (await screen.findByText("Pricing to review")).closest("a");
    expect(pricingCard?.getAttribute("href")).toBe("/dashboard/ecosystem/pricing");
    const sourcesCard = screen.getByText("Active sources").closest("a");
    expect(sourcesCard?.getAttribute("href")).toBe("/dashboard/ecosystem/sources");
  });
});
