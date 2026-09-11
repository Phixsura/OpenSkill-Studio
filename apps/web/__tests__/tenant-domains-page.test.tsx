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
vi.mock("@/lib/use-me", () => ({
  useImpersonation: () => false,
  useTenantRole: () => "owner",
  usePlatformAdmin: () => false,
}));

import TenantDomainsPage from "@/app/(dashboard)/dashboard/tenant/[tenantId]/domains/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

describe("TenantDomainsPage (R392 — the M34 token trim)", () => {
  beforeEach(() => api.mockReset());

  it("trims pasted verification tokens before sending (each doomed attempt burns the 6/hr budget)", async () => {
    api.mockImplementation((rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path === "/tenants/t-1/domains")
        return Promise.resolve({
          data: [
            {
              id: "d-1",
              hostname: "ai.acme.com",
              status: "pending_verification",
              tls_status: "unmanaged",
              verify_attempts: 0,
              created_at: "2026-09-01T00:00:00Z",
            },
          ],
        });
      return Promise.resolve({ data: {} });
    });
    render(<TenantDomainsPage />, { wrapper: wrapper() });
    await screen.findByText("ai.acme.com");
    const tokenInput = screen.getByPlaceholderText(/token/i);
    fireEvent.change(tokenInput, { target: { value: "  osk-verify-abc123  \n" } });
    fireEvent.click(screen.getByRole("button", { name: /verify/i }));
    await waitFor(() => {
      const call = api.mock.calls.find((c) => String(c[0]).endsWith("/domains/d-1/verify"));
      expect(call).toBeTruthy();
      const body = JSON.parse((call![1] as RequestInit).body as string);
      expect(body.token).toBe("osk-verify-abc123");
    });
  });
});
