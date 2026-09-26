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
  usePathname: () => "/dashboard/ecosystem/compare",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ComparePage from "@/app/(dashboard)/dashboard/ecosystem/compare/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => vi.clearAllMocks());

describe("Ecosystem compare & estimate page (ADR-016 §19)", () => {
  it("renders side-by-side table with prices and benchmark dims", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/compare"))
        return Promise.resolve({
          data: [
            {
              entity_kind: "model",
              entity_id: "A".repeat(26),
              canonical_name: "AlphaGen",
              lifecycle_status: "verified",
              prices: {
                image: { unit: "image", price: 0.04, currency: "USD", approved: true },
              },
              availability_status: { state: "operational" },
              benchmark: {
                run_id: "r1",
                finished_at: "2026-09-20T00:00:00Z",
                dimension_scores: { quality: 4.2 },
              },
            },
            {
              entity_kind: "model",
              entity_id: "B".repeat(26),
              canonical_name: "BetaGen",
              lifecycle_status: "discovered",
              prices: {},
              availability_status: null,
              benchmark: null,
            },
          ],
        });
      return Promise.resolve({ data: [] });
    });
    render(<ComparePage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByPlaceholderText(/entity ids/), {
      target: { value: `${"A".repeat(26)},${"B".repeat(26)}` },
    });
    fireEvent.click(screen.getByText("Compare", { selector: "button" }));
    expect(await screen.findByText("AlphaGen")).toBeDefined();
    expect(screen.getByText("BetaGen")).toBeDefined();
    expect(screen.getByText(/Price \/ image/)).toBeDefined();
    expect(screen.getByText(/✓ approved/)).toBeDefined();
    expect(screen.getByText(/Benchmark · quality/)).toBeDefined();
  });

  it("estimator posts workload and shows flagged missing units", async () => {
    api.mockImplementation((path: string) => {
      if (path === "/ecosystem/pricing/estimate")
        return Promise.resolve({
          data: [
            {
              entity_id: "A".repeat(26),
              estimated_total: 1.4,
              currency: "USD",
              fully_priced: false,
              all_prices_approved: false,
              missing_units: ["token_output"],
              breakdown: [
                {
                  unit: "token_input",
                  quantity: 1000000,
                  unit_price: 0.0000014,
                  line_total: 1.4,
                  approved: false,
                },
              ],
            },
          ],
        });
      return Promise.resolve({ data: [] });
    });
    render(<ComparePage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByPlaceholderText(/entity ids/), {
      target: { value: "A".repeat(26) },
    });
    fireEvent.click(screen.getByText("Estimate cost"));
    expect(await screen.findByText(/1.4 USD/)).toBeDefined();
    expect(screen.getByText(/missing: token_output/)).toBeDefined();
    expect(
      api.mock.calls.some(
        (c) => c[0] === "/ecosystem/pricing/estimate" && (c[1] as RequestInit)?.method === "POST",
      ),
    ).toBe(true);
  });

  it("mixed-currency estimates show the flag instead of a bogus total", async () => {
    api.mockImplementation((path: string, init?: RequestInit) => {
      if (path.includes("/pricing/estimate"))
        return Promise.resolve({
          data: [
            {
              entity_kind: "model",
              entity_id: "M".repeat(26),
              estimated_total: null,
              currency: null,
              mixed_currency: true,
              breakdown: [
                {
                  unit: "token_input",
                  quantity: 1000,
                  unit_price: 0.01,
                  currency: "USD",
                  approved: true,
                  line_total: 10,
                },
                {
                  unit: "image",
                  quantity: 2,
                  unit_price: 0.05,
                  currency: "EUR",
                  approved: true,
                  line_total: 0.1,
                },
              ],
              missing_units: [],
              fully_priced: true,
              all_prices_approved: true,
            },
          ],
        });
      return Promise.resolve({ data: [] });
    });
    render(<ComparePage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByPlaceholderText(/entity ids/), {
      target: { value: "M".repeat(26) },
    });
    fireEvent.click(screen.getByText("Estimate cost"));
    expect(await screen.findByText(/mixed currencies — see lines/)).toBeDefined();
    expect(screen.getByText(/multiple currencies; no single total/)).toBeDefined();
  });

  it("comparison shows human-arbitrated curated facts", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/compare"))
        return Promise.resolve({
          data: [
            {
              entity_kind: "model",
              entity_id: "A".repeat(26),
              canonical_name: "GenA",
              lifecycle_status: "verified",
              metadata: { curated: { license: { value: "MIT" } } },
              prices: {},
              availability_status: null,
              benchmark: null,
            },
            {
              entity_kind: "model",
              entity_id: "B".repeat(26),
              canonical_name: "GenB",
              lifecycle_status: "verified",
              metadata: null,
              prices: {},
              availability_status: null,
              benchmark: null,
            },
          ],
        });
      return Promise.resolve({ data: [] });
    });
    render(<ComparePage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByPlaceholderText(/entity ids/), {
      target: { value: `${"A".repeat(26)},${"B".repeat(26)}` },
    });
    fireEvent.click(screen.getByText("Compare", { selector: "button" }));
    expect(await screen.findByText("Curated facts")).toBeDefined();
    expect(screen.getByText("MIT")).toBeDefined();
  });

  it("renders the 30-day stability strip per entity (R268)", async () => {
    api.mockImplementation((path: string) => {
      if (path.startsWith("/ecosystem/compare"))
        return Promise.resolve({
          data: [
            {
              entity_kind: "model",
              entity_id: "A".repeat(26),
              canonical_name: "StripGen",
              lifecycle_status: "verified",
              prices: {},
              availability_status: { status: "operational" },
              benchmark: null,
              metadata: null,
            },
          ],
        });
      if (path.includes("/pricing/availability/uptime"))
        return Promise.resolve({
          data: {
            current_status: "operational",
            uptime_pct: 96.7,
            incidents: 1,
            coverage_pct: 88,
            daily: [
              { date: "2026-09-24", worst_status: "operational" },
              { date: "2026-09-25", worst_status: "unreachable" },
            ],
          },
        });
      return Promise.resolve({ data: [] });
    });
    render(<ComparePage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByPlaceholderText(/entity ids/), {
      target: { value: "A".repeat(26) },
    });
    fireEvent.click(screen.getByText("Compare", { selector: "button" }));
    expect(await screen.findByText("StripGen")).toBeDefined();
    expect(await screen.findByTitle("2026-09-25: unreachable")).toBeDefined();
    expect(screen.getByTitle("2026-09-24: operational")).toBeDefined();
    expect(screen.getByText(/96.7% uptime \(30d\)/)).toBeDefined();
  });
});
