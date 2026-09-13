import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ tenantId: "t-1" }) }));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));
const roleState = vi.hoisted(() => ({
  impersonating: false,
  role: "owner" as string | null,
  platformAdmin: false,
}));
vi.mock("@/lib/use-me", () => ({
  useImpersonation: () => roleState.impersonating,
  useTenantRole: () => roleState.role,
  usePlatformAdmin: () => roleState.platformAdmin,
}));

import TenantMembersPage from "@/app/(dashboard)/dashboard/tenant/[tenantId]/members/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function route() {
  api.mockImplementation((rawPath: unknown) => {
    const path = String(rawPath ?? "");
    if (path === "/tenants/t-1/members")
      return Promise.resolve({
        data: [
          { id: "m-1", user_id: "u-9x", role: "billing_admin", created_at: "2026-09-01T00:00:00Z" },
        ],
      });
    return Promise.resolve({ data: {} });
  });
}

describe("TenantMembersPage gating (R391)", () => {
  beforeEach(() => {
    api.mockReset();
    roleState.impersonating = false;
    roleState.role = "owner";
    roleState.platformAdmin = false;
  });

  it("billing_admin (non-owner) cannot add members", async () => {
    roleState.role = "billing_admin";
    route();
    render(<TenantMembersPage />, { wrapper: wrapper() });
    await screen.findByText(/u-9x/);
    const add = screen.getByRole("button", { name: /add/i }) as HTMLButtonElement;
    expect(add.disabled).toBe(true);
  });

  it("a PLATFORM ADMIN without a membership row can manage (R113[L6])", async () => {
    roleState.role = null;
    roleState.platformAdmin = true;
    route();
    render(<TenantMembersPage />, { wrapper: wrapper() });
    await screen.findByText(/u-9x/);
    const input = screen.getByPlaceholderText(/user id/i);
    fireEvent.change(input, { target: { value: "01JUSERAAAAAAAAAAAAAAAAAAA" } });
    const add = screen.getByRole("button", { name: /add/i }) as HTMLButtonElement;
    expect(add.disabled).toBe(false);
    fireEvent.click(add);
    await waitFor(() => {
      expect(
        api.mock.calls.some(
          (c) =>
            String(c[0]) === "/tenants/t-1/members" && (c[1] as RequestInit)?.method === "POST",
        ),
      ).toBe(true);
    });
  });

  it("impersonation disables add even for an owner (M27)", async () => {
    roleState.impersonating = true;
    route();
    render(<TenantMembersPage />, { wrapper: wrapper() });
    await screen.findByText(/u-9x/);
    fireEvent.change(screen.getByPlaceholderText(/user id/i), {
      target: { value: "01JUSERAAAAAAAAAAAAAAAAAAA" },
    });
    const add = screen.getByRole("button", { name: /add/i }) as HTMLButtonElement;
    expect(add.disabled).toBe(true);
  });
});
