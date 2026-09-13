import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ tenantId: "t-1" }),
}));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

const roleState = vi.hoisted(() => ({ impersonating: false, role: "owner" as string | null }));
vi.mock("@/lib/use-me", () => ({
  useImpersonation: () => roleState.impersonating,
  useTenantRole: () => roleState.role,
  usePlatformAdmin: () => false,
}));

import TenantBillingPage from "@/app/(dashboard)/dashboard/tenant/[tenantId]/billing/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function route(sub: Record<string, unknown> | null) {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path === "/tenants/t-1/subscription") return Promise.resolve({ data: sub });
    if (path === "/tenants/t-1") return Promise.resolve({ data: { currency: "USD" } });
    if (path.startsWith("/tenants/t-1/invoices"))
      return Promise.resolve({ data: [], meta: { has_more: false } });
    if (path === "/plans") return Promise.resolve({ data: [] });
    return Promise.resolve({ data: null });
  });
}

const LIVE_SUB = {
  id: "s-1",
  plan_key: "school",
  plan_name: "School",
  status: "active",
  interval: "month",
  seat_quantity: 0,
  currency: "USD",
  current_period_start: "2026-09-01T00:00:00Z",
  current_period_end: "2026-10-01T00:00:00Z",
  cancel_at_period_end: false,
  provider: "manual",
};

describe("TenantBillingPage cancel gating (R382 — M9/M27 write controls)", () => {
  beforeEach(() => {
    api.mockReset();
    roleState.impersonating = false;
    roleState.role = "owner";
  });

  it("an owner can cancel; the POST goes to the cancel endpoint", async () => {
    route(LIVE_SUB);
    render(<TenantBillingPage />, { wrapper: wrapper() });
    const btn = (await screen.findByRole("button", {
      name: /cancel at period end/i,
    })) as HTMLButtonElement;
    expect(btn.disabled).toBe(false);
    fireEvent.click(btn);
    await waitFor(() => {
      expect(
        api.mock.calls.some(
          (c) =>
            String(c[0]) === "/tenants/t-1/subscription/cancel" &&
            (c[1] as RequestInit)?.method === "POST",
        ),
      ).toBe(true);
    });
  });

  it("billing_admin sees cancel DISABLED (M9: owner-only server-side)", async () => {
    roleState.role = "billing_admin";
    route(LIVE_SUB);
    render(<TenantBillingPage />, { wrapper: wrapper() });
    const btn = (await screen.findByRole("button", {
      name: /cancel at period end/i,
    })) as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });

  it("an impersonated session sees cancel DISABLED (M27: read-only)", async () => {
    roleState.impersonating = true;
    route(LIVE_SUB);
    render(<TenantBillingPage />, { wrapper: wrapper() });
    const btn = (await screen.findByRole("button", {
      name: /cancel at period end/i,
    })) as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });

  it("a cancel_at_period_end sub shows the banner instead of the button", async () => {
    route({ ...LIVE_SUB, cancel_at_period_end: true });
    render(<TenantBillingPage />, { wrapper: wrapper() });
    expect(await screen.findByText(/cancels at period end/i)).toBeTruthy();
    expect(screen.queryByRole("button", { name: /cancel at period end/i })).toBeNull();
  });
});
