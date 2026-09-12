import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({}) }));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));
vi.mock("@/lib/use-me", () => ({
  useImpersonation: () => false,
  useTenantRole: () => null,
  usePlatformAdmin: () => true,
}));

import PlatformSettlementsPage from "@/app/(dashboard)/platform/settlements/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

function statement(status: string) {
  return {
    id: "st-1",
    beneficiary_type: "partner",
    partner_id: "p-1",
    partner_name: "Acme Partner",
    period: "2026-08",
    status,
    currency: "USD",
    gross_revenue_minor: 100000,
    refunds_minor: 0,
    share_total_minor: 10000,
    opening_adjustments_minor: 0,
    manual_adjustments_minor: 0,
    net_amount_minor: 10000,
    external_payment_ref: null,
  };
}

function route(status: string) {
  api.mockImplementation((rawPath: unknown, init?: RequestInit) => {
    const path = String(rawPath ?? "");
    if (path.includes("/platform/settlements") && !init?.method)
      return Promise.resolve({ data: [statement(status)], meta: { has_more: false } });
    return Promise.resolve({ data: {} });
  });
}

describe("PlatformSettlementsPage action ladder (R397)", () => {
  beforeEach(() => api.mockReset());

  it("draft offers ONLY finalize; the POST hits the finalize action", async () => {
    route("draft");
    render(<PlatformSettlementsPage />, { wrapper: wrapper() });
    const fin = await screen.findByRole("button", { name: /finalize/i });
    expect(screen.queryByRole("button", { name: /approve/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /mark paid/i })).toBeNull();
    fireEvent.click(fin);
    await waitFor(() => {
      expect(
        api.mock.calls.some(
          (c) =>
            String(c[0]) === "/platform/settlements/st-1/finalize" &&
            (c[1] as RequestInit)?.method === "POST",
        ),
      ).toBe(true);
    });
  });

  it("mark-paid requires a payment ref and sends it in the body", async () => {
    route("approved");
    render(<PlatformSettlementsPage />, { wrapper: wrapper() });
    const pay = (await screen.findByRole("button", {
      name: /mark paid/i,
    })) as HTMLButtonElement;
    expect(pay.disabled).toBe(true); // no ref typed → disabled
    fireEvent.change(screen.getByPlaceholderText(/payment ref/i), {
      target: { value: "WIRE-88" },
    });
    expect(pay.disabled).toBe(false);
    fireEvent.click(pay);
    await waitFor(() => {
      const post = api.mock.calls.find((c) => String(c[0]).endsWith("/mark-paid"));
      expect(post).toBeTruthy();
      const body = JSON.parse((post![1] as RequestInit).body as string);
      expect(body.external_payment_ref).toBe("WIRE-88");
    });
  });

  it("a paid statement offers no actions", async () => {
    route("paid_externally");
    render(<PlatformSettlementsPage />, { wrapper: wrapper() });
    await screen.findByText(/acme partner/i);
    for (const name of [/finalize/i, /approve/i, /mark paid/i]) {
      expect(screen.queryByRole("button", { name })).toBeNull();
    }
  });
});
