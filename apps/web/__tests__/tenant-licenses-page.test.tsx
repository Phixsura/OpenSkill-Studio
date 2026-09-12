import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ tenantId: "t-1" }) }));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  },
}));
vi.mock("@/lib/use-me", () => ({
  useImpersonation: () => false,
  useTenantRole: () => "owner",
  usePlatformAdmin: () => false,
}));

import TenantLicensesPage from "@/app/(dashboard)/dashboard/tenant/[tenantId]/licenses/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function route(grant: Record<string, unknown>, orgs: unknown[]) {
  api.mockImplementation((rawPath: unknown, init?: RequestInit) => {
    const path = String(rawPath ?? "");
    if (path === "/tenants/t-1/licenses") return Promise.resolve({ data: [grant] });
    if (path === "/tenants/t-1/purchases")
      return Promise.resolve({ data: [], meta: { has_more: false } });
    if (path === "/orgs") return Promise.resolve({ data: orgs });
    if (init?.method === "POST") return Promise.resolve({ data: {} });
    return Promise.resolve({ data: [] });
  });
}

const GRANT = {
  id: "g-1",
  listing_id: null,
  product_type: "learning_path",
  product_id: "lp-9",
  org_id: null,
  scope: "tenant",
  seat_limit: null,
  status: "active",
  source: "manual",
  expires_at: null,
  created_at: "2026-09-01T00:00:00Z",
};

describe("TenantLicensesPage install fallback (R396 — L0/H2/H3 + R130[32])", () => {
  beforeEach(() => api.mockReset());

  it("a tenant-scope manual grant installs via THIS tenant's admin org with product_id", async () => {
    route(GRANT, [
      { id: "o-foreign", name: "Foreign", role: "owner", tenant_id: "t-OTHER" },
      { id: "o-member", name: "Member", role: "member", tenant_id: "t-1" },
      { id: "o-admin", name: "Mine", role: "admin", tenant_id: "t-1" },
    ]);
    render(<TenantLicensesPage />, { wrapper: wrapper() });
    const btn = await screen.findByRole("button", { name: /install/i });
    fireEvent.click(btn);
    await waitFor(() => {
      const post = api.mock.calls.find((c) => (c[1] as RequestInit | undefined)?.method === "POST");
      expect(post).toBeTruthy();
      // R130[32]: never the foreign-tenant org, never the plain member org
      expect(String(post![0])).toBe("/orgs/o-admin/learning-paths/install");
      const body = JSON.parse((post![1] as RequestInit).body as string);
      expect(body).toEqual({ product_id: "lp-9" }); // listing-less → product_id
    });
  });

  it("with no admin org in THIS tenant the install fails with NO_ORG, no POST", async () => {
    route(GRANT, [{ id: "o-foreign", name: "Foreign", role: "owner", tenant_id: "t-OTHER" }]);
    render(<TenantLicensesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: /install/i }));
    await waitFor(() => {
      const posts = api.mock.calls.filter(
        (c) => (c[1] as RequestInit | undefined)?.method === "POST",
      );
      expect(posts).toHaveLength(0); // never a foreign-org POST
    });
  });

  it("a listing-backed grant installs with listing_id", async () => {
    route({ ...GRANT, listing_id: "lst-5" }, [
      { id: "o-admin", name: "Mine", role: "owner", tenant_id: "t-1" },
    ]);
    render(<TenantLicensesPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByRole("button", { name: /install/i }));
    await waitFor(() => {
      const post = api.mock.calls.find((c) => (c[1] as RequestInit | undefined)?.method === "POST");
      const body = JSON.parse((post![1] as RequestInit).body as string);
      expect(body).toEqual({ listing_id: "lst-5" });
    });
  });
});
