import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ partnerId: "pt-1" }),
}));
vi.mock("@/lib/api", () => {
  class MockApiError extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  }
  return { apiWithAuth: vi.fn(), ApiError: MockApiError };
});

import PartnerOverviewPage from "@/app/(dashboard)/partner/[partnerId]/page";
import PartnerTenantsPage from "@/app/(dashboard)/partner/[partnerId]/tenants/page";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const PARTNER = {
  id: "pt-1",
  name: "Acme Partners",
  slug: "acme",
  partner_type: "reseller",
  status: "active",
  currency: "EUR",
  contact_email: null,
  unsettled_accruals_minor: 123400,
};

const ENTRIES = [
  { id: "e-1", share_amount_minor: 5000, currency: "EUR", period: "2026-08", status: "accrued" },
  { id: "e-2", share_amount_minor: 700, currency: "EUR", period: "2026-07", status: "settled" },
];

beforeEach(() => vi.clearAllMocks());

describe("PartnerOverviewPage (R412)", () => {
  it("unsettled accruals come from the SERVER aggregate, not a client sum of visible entries", async () => {
    api.mockImplementation((rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path === "/partners/pt-1") return Promise.resolve({ data: PARTNER });
      if (path.includes("revenue-share-entries")) return Promise.resolve({ data: ENTRIES });
      return Promise.resolve({ data: null });
    });
    render(<PartnerOverviewPage />, { wrapper: wrapper() });
    await screen.findByText("Acme Partners");
    const body = document.body.textContent ?? "";
    // server aggregate 1234.00 — NOT the 57.00 sum of the two visible rows
    expect(body).toContain(formatMinor(123400, "EUR"));
    expect(body).not.toContain(formatMinor(5700, "EUR"));
    // entry rows render their own money
    expect(body).toContain(formatMinor(5000, "EUR"));
    expect(body).toContain("2026-08");
  });

  it("failed entries fetch shows an error, never an authoritative 'No entries yet.'", async () => {
    api.mockImplementation((rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path === "/partners/pt-1") return Promise.resolve({ data: PARTNER });
      return Promise.reject(new Error("entries down"));
    });
    render(<PartnerOverviewPage />, { wrapper: wrapper() });
    await screen.findByText("Acme Partners");
    await waitFor(() => {
      expect(document.body.textContent).toMatch(/failed|error|down/i);
    });
    expect(screen.queryByText("No entries yet.")).toBeNull();
  });
});

describe("PartnerTenantsPage (R412)", () => {
  it("renders attributed tenants with plan fallback and requests page 2 via the pager", async () => {
    const calls: string[] = [];
    api.mockImplementation((rawPath: unknown) => {
      calls.push(String(rawPath ?? ""));
      return Promise.resolve({
        data: [
          {
            tenant_id: "t-1",
            name: "School A",
            slug: "school-a",
            status: "active",
            plan_key: "school",
            created_at: "2026-08-01T00:00:00Z",
          },
          {
            tenant_id: "t-2",
            name: "School B",
            slug: "school-b",
            status: "trial",
            plan_key: null,
            created_at: "2026-08-02T00:00:00Z",
          },
        ],
        meta: { has_more: true },
      });
    });
    render(<PartnerTenantsPage />, { wrapper: wrapper() });
    await screen.findByText("School A");
    expect(document.body.textContent ?? "").toContain("—"); // null plan
    fireEvent.click(screen.getByRole("button", { name: /next/i }));
    await waitFor(() => {
      expect(calls.some((c) => c.includes("page=2"))).toBe(true);
    });
  });

  it("403 renders the admins-only note, NOT the provision empty state (R101[M29])", async () => {
    api.mockImplementation(() =>
      Promise.reject(
        new (ApiError as new (s: number, c: string, m: string) => Error)(403, "FORBIDDEN", "nope"),
      ),
    );
    render(<PartnerTenantsPage />, { wrapper: wrapper() });
    expect(
      await screen.findByText("Attributed tenants are visible to partner admins only."),
    ).toBeTruthy();
    expect(screen.queryByText(/Provision one from the Provision tab/)).toBeNull();
  });

  it("non-403 errors surface via QueryError, empty page shows the provision hint", async () => {
    api.mockImplementation(() => Promise.reject(new Error("boom")));
    render(<PartnerTenantsPage />, { wrapper: wrapper() });
    await waitFor(() => {
      expect(document.body.textContent).toMatch(/attributed tenants/i);
      expect(document.body.textContent).toMatch(/failed|error|boom/i);
    });
    vi.clearAllMocks();
    api.mockImplementation(() => Promise.resolve({ data: [], meta: { has_more: false } }));
    render(<PartnerTenantsPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/No attributed tenants\. Provision one/)).toBeTruthy();
  });
});
