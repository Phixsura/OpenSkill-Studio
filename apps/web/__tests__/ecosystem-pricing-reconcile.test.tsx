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
  usePathname: () => "/dashboard/ecosystem/pricing",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import PricingPage from "@/app/(dashboard)/dashboard/ecosystem/pricing/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const OBS = "P".repeat(26);

beforeEach(() => {
  vi.clearAllMocks();
  api.mockImplementation((path: string, init?: RequestInit) => {
    if (path.startsWith("/ecosystem/pricing/observations?") && !init)
      return Promise.resolve({
        data: [
          {
            id: OBS,
            entity_kind: "model",
            entity_id: "M".repeat(26),
            unit: "per_1k_tokens_input",
            region: null,
            price: "0.0100",
            currency: "USD",
            observed_at: "2026-09-20T00:00:00Z",
            reconciliation_status: "unreviewed",
            approved_cost_rate_id: null,
          },
        ],
      });
    return Promise.resolve({ data: {} });
  });
});

describe("Pricing reconciliation wiring (ADR-016 §13 UI)", () => {
  it("Approve POSTs decision=approve with the typed provider key", async () => {
    render(<PricingPage />, { wrapper: wrapper() });
    fireEvent.change(await screen.findByPlaceholderText(/provider key for approval/), {
      target: { value: "openai" },
    });
    fireEvent.click(screen.getByText("Approve → billing"));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === `/ecosystem/pricing/observations/${OBS}/reconcile` &&
        (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(body.decision).toBe("approve");
    expect(body.provider_key).toBe("openai");
  });

  it("Reject never sends a provider key (no accidental billing mint)", async () => {
    render(<PricingPage />, { wrapper: wrapper() });
    fireEvent.change(await screen.findByPlaceholderText(/provider key for approval/), {
      target: { value: "openai" },
    });
    fireEvent.click(screen.getByText("Reject"));
    await new Promise((r) => setTimeout(r, 0));
    const call = api.mock.calls.find(
      (c) =>
        c[0] === `/ecosystem/pricing/observations/${OBS}/reconcile` &&
        (c[1] as RequestInit)?.method === "POST",
    );
    expect(call).toBeDefined();
    const body = JSON.parse((call![1] as RequestInit).body as string);
    expect(body.decision).toBe("reject");
    expect(body.provider_key).toBeNull();
  });
});
