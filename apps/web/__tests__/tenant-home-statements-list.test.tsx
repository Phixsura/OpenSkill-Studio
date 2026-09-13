import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  useParams: () => ({ tenantId: "t-1", partnerId: "pt-1" }),
}));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import PartnerStatementsPage from "@/app/(dashboard)/partner/[partnerId]/statements/page";
import TenantOverviewPage from "@/app/(dashboard)/dashboard/tenant/[tenantId]/page";
import { apiWithAuth } from "@/lib/api";
import { formatMinor } from "@/lib/cp";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => vi.clearAllMocks());

const TENANT = {
  id: "t-1",
  name: "North",
  slug: "north",
  status: "active",
  account_type: "direct",
  currency: "USD",
  timezone: "Asia/Tokyo",
  billing_email: null,
  trial_ends_at: null,
  created_at: "2026-01-01T00:00:00Z",
};

const ENT = {
  plan: { key: "school", version: 3 },
  entitlements: {
    max_active_learners: { value: 100, usage: 42, source: "plan", enforcement: "hard" },
    api_access: { value: true, usage: null, source: "plan", enforcement: "hard" },
    sso: { value: false, usage: null, source: "plan", enforcement: "hard" },
    max_storage_gb: { value: null, usage: "7", source: "override", enforcement: "soft" },
  },
};

function routeTenant(t: Record<string, unknown>, entFail = false) {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path === "/tenants/t-1") return Promise.resolve({ data: t });
    if (path === "/tenants/t-1/entitlements") {
      if (entFail) return Promise.reject(new Error("ent down"));
      return Promise.resolve({ data: ENT });
    }
    return Promise.resolve({ data: null });
  });
}

describe("TenantOverviewPage (R415)", () => {
  it("entitlement value semantics: null=unlimited, booleans as ✓/✗, numbers verbatim, soft tag", async () => {
    routeTenant(TENANT);
    render(<TenantOverviewPage />, { wrapper: wrapper() });
    await screen.findByText("North");
    await screen.findByText("max_active_learners");
    const rows = Array.from(document.querySelectorAll("tbody tr"));
    const cells = (frag: string) => {
      const r = rows.find((x) => x.textContent?.includes(frag));
      return Array.from(r?.children ?? []).map((c) => c.textContent);
    };
    expect(cells("max_active_learners").slice(1, 3)).toEqual(["100", "42"]);
    expect(cells("api_access")[1]).toBe("✓");
    expect(cells("sso")[1]).toBe("✗");
    expect(cells("max_storage_gb")[1]).toBe("unlimited");
    expect(cells("max_storage_gb")[3]).toBe("override (soft)");
    expect(document.body.textContent ?? "").toContain("school v3");
    // no banners for an active tenant
    expect(screen.queryByText(/Trial ends/)).toBeNull();
    expect(screen.queryByText(/suspended/i)).toBeNull();
  });

  it("trial and suspended banners are status-gated", async () => {
    routeTenant({ ...TENANT, status: "trial", trial_ends_at: "2026-10-01T00:00:00Z" });
    const r1 = render(<TenantOverviewPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/Trial ends/)).toBeTruthy();
    r1.unmount();
    routeTenant({ ...TENANT, status: "suspended" });
    render(<TenantOverviewPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/This account is suspended/)).toBeTruthy();
    expect(screen.queryByText(/Trial ends/)).toBeNull();
  });

  it("failed entitlements fetch shows an error, never a bare 'Plan —' (R113[M29])", async () => {
    routeTenant(TENANT, true);
    render(<TenantOverviewPage />, { wrapper: wrapper() });
    await screen.findByText("North");
    await waitFor(() => {
      expect(document.body.textContent).toMatch(/entitlements/i);
      expect(document.body.textContent).toMatch(/failed|error|down/i);
    });
  });
});

describe("PartnerStatementsPage (R415)", () => {
  it("rows: money in statement currency, period links to detail, null payment ref as em dash", async () => {
    api.mockResolvedValue({
      data: [
        {
          id: "st-1",
          period: "2026-08",
          status: "finalized",
          currency: "EUR",
          share_total_minor: 100000,
          net_amount_minor: 99800,
          external_payment_ref: "SEPA-1",
        },
        {
          id: "st-2",
          period: "2026-07",
          status: "draft",
          currency: "EUR",
          share_total_minor: 500,
          net_amount_minor: 500,
          external_payment_ref: null,
        },
      ],
    });
    render(<PartnerStatementsPage />, { wrapper: wrapper() });
    await screen.findByText("2026-08");
    const body = document.body.textContent ?? "";
    expect(body).toContain(formatMinor(100000, "EUR"));
    expect(body).toContain(formatMinor(99800, "EUR"));
    expect(body).toContain("SEPA-1");
    expect(body).toContain("—");
    expect(screen.getByText("2026-08").closest("a")?.getAttribute("href")).toBe(
      "/partner/pt-1/statements/st-1",
    );
  });

  it("failed fetch surfaces an error, never 'No statements yet.' (R113[M24])", async () => {
    api.mockRejectedValue(new Error("stmts down"));
    render(<PartnerStatementsPage />, { wrapper: wrapper() });
    await waitFor(() => {
      expect(document.body.textContent).toMatch(/statements/i);
      expect(document.body.textContent).toMatch(/failed|error|down/i);
    });
    expect(screen.queryByText("No statements yet.")).toBeNull();
  });
});
