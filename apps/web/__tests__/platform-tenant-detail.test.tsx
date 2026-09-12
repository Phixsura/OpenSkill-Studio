import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ tenantId: "t-1" }) }));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));
const roleState = vi.hoisted(() => ({ impersonating: false }));
vi.mock("@/lib/use-me", () => ({
  useImpersonation: () => roleState.impersonating,
  useTenantRole: () => null,
  usePlatformAdmin: () => true,
}));

import PlatformTenantDetail from "@/app/(dashboard)/platform/tenants/[tenantId]/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function route(status: string) {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path.includes("/platform/tenants/t-1"))
      return Promise.resolve({
        data: {
          tenant: {
            id: "t-1",
            name: "Acme",
            slug: "acme",
            status,
            currency: "USD",
            timezone: "UTC",
            created_at: "2026-01-01T00:00:00Z",
          },
          orgs: [],
          subscription: null,
          entitlements: {},
        },
      });
    return Promise.resolve({ data: {} });
  });
}

describe("PlatformTenantDetail lifecycle controls (R393 — L18 + M27)", () => {
  beforeEach(() => {
    api.mockReset();
    roleState.impersonating = false;
  });

  it("terminal tenants (cancelled) hide BOTH lifecycle controls (L18)", async () => {
    route("cancelled");
    render(<PlatformTenantDetail />, { wrapper: wrapper() });
    expect(await screen.findByText(/no lifecycle actions available/i)).toBeTruthy();
    expect(screen.queryByRole("button", { name: /suspend/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /reactivate/i })).toBeNull();
  });

  it("suspend requires a reason and is read-only under impersonation (M27)", async () => {
    route("active");
    render(<PlatformTenantDetail />, { wrapper: wrapper() });
    const btn = (await screen.findByRole("button", {
      name: /suspend/i,
    })) as HTMLButtonElement;
    expect(btn.disabled).toBe(true); // no reason yet
    roleState.impersonating = true;
    route("active");
    render(<PlatformTenantDetail />, { wrapper: wrapper() });
    const btns = (await screen.findAllByRole("button", {
      name: /suspend/i,
    })) as HTMLButtonElement[];
    expect(btns.every((b) => b.disabled)).toBe(true);
  });

  it("a suspended tenant offers reactivate, not suspend", async () => {
    route("suspended");
    render(<PlatformTenantDetail />, { wrapper: wrapper() });
    expect(await screen.findByRole("button", { name: /reactivate/i })).toBeTruthy();
    expect(screen.queryByRole("button", { name: /suspend/i })).toBeNull();
  });
});
