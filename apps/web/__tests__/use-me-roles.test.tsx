import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { MeExtended } from "@/lib/cp";

const apiMock = vi.hoisted(() => vi.fn());
vi.mock("@/lib/api", () => ({ apiWithAuth: apiMock }));

import { useImpersonation, usePlatformAdmin, useTenantRole } from "@/lib/use-me";

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

function me(overrides: Partial<MeExtended>): { data: Partial<MeExtended> } {
  return { data: { role: "user", platform_roles: [], tenant_memberships: [], ...overrides } };
}

describe("use-me role hooks (R368 — role-conditional UI gating)", () => {
  beforeEach(() => apiMock.mockReset());

  it("useImpersonation: true only when the session carries the banner data", async () => {
    apiMock.mockResolvedValueOnce(me({ impersonation: { admin_email: "a@x" } } as never));
    const { result } = renderHook(() => useImpersonation(), { wrapper });
    await waitFor(() => expect(result.current).toBe(true));
  });

  it("useImpersonation: false for a plain session (write controls stay on)", async () => {
    apiMock.mockResolvedValueOnce(me({}));
    const { result } = renderHook(() => useImpersonation(), { wrapper });
    await waitFor(() => expect(apiMock).toHaveBeenCalled());
    expect(result.current).toBe(false);
  });

  it("usePlatformAdmin: admin role OR platform_admin platform-role (R113[L6])", async () => {
    apiMock.mockResolvedValueOnce(me({ role: "admin" }));
    const a = renderHook(() => usePlatformAdmin(), { wrapper });
    await waitFor(() => expect(a.result.current).toBe(true));

    apiMock.mockResolvedValueOnce(me({ platform_roles: ["platform_admin"] }));
    const b = renderHook(() => usePlatformAdmin(), { wrapper });
    await waitFor(() => expect(b.result.current).toBe(true));

    // billing_ops alone is NOT platform admin; neither is a plain user
    apiMock.mockResolvedValueOnce(me({ platform_roles: ["billing_ops"] }));
    const c = renderHook(() => usePlatformAdmin(), { wrapper });
    await waitFor(() => expect(apiMock).toHaveBeenCalledTimes(3));
    expect(c.result.current).toBe(false);
  });

  it("useTenantRole: resolves THIS tenant's role, null for non-members and null ids", async () => {
    const memberships = [
      { tenant_id: "t1", role: "billing_admin" },
      { tenant_id: "t2", role: "owner" },
    ];
    apiMock.mockResolvedValue(me({ tenant_memberships: memberships } as never));
    const a = renderHook(() => useTenantRole("t2"), { wrapper });
    await waitFor(() => expect(a.result.current).toBe("owner"));
    const b = renderHook(() => useTenantRole("t1"), { wrapper });
    await waitFor(() => expect(b.result.current).toBe("billing_admin"));
    const c = renderHook(() => useTenantRole("t3"), { wrapper });
    await waitFor(() => expect(apiMock).toHaveBeenCalled());
    expect(c.result.current).toBe(null);
    const d = renderHook(() => useTenantRole(null), { wrapper });
    expect(d.result.current).toBe(null);
    expect(apiMock).toHaveBeenCalledWith("/auth/me");
  });
});
