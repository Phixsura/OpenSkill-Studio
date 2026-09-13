import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({ useParams: () => ({ partnerId: "p-1" }) }));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import PartnerProvisionPage from "@/app/(dashboard)/partner/[partnerId]/provision/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

describe("PartnerProvisionPage (R395 — L6 blueprint filter + H7 idempotency key)", () => {
  beforeEach(() => api.mockReset());

  it("hides inactive blueprints and sends the ALL-PARAMS idempotency key", async () => {
    api.mockImplementation((rawPath: unknown, init?: RequestInit) => {
      const path = String(rawPath ?? "");
      if (path.includes("/blueprints"))
        return Promise.resolve({
          data: [
            { id: "bp-live", name: "Live BP", is_active: true },
            { id: "bp-dead", name: "Dead BP", is_active: false },
          ],
        });
      if (path === "/partners/p-1/provision-runs" && init?.method === "POST")
        return Promise.resolve({
          data: { id: "run-1", status: "pending", steps: [] },
        });
      if (path.includes("/provision-runs/run-1"))
        return Promise.resolve({
          data: {
            id: "run-1",
            status: "completed",
            steps: [{ step: "create_tenant", status: "done", error: null }],
          },
        });
      return Promise.resolve({ data: [] });
    });
    render(<PartnerProvisionPage />, { wrapper: wrapper() });
    // L6: the dead blueprint never appears as an option
    await screen.findByText("Live BP");
    expect(screen.queryByText("Dead BP")).toBeNull();

    fireEvent.change(screen.getByPlaceholderText(/name/i), {
      target: { value: "Acme School" },
    });
    fireEvent.change(screen.getByPlaceholderText(/slug/i), {
      target: { value: "acme-school" },
    });
    const select = screen.getByRole("combobox") as HTMLSelectElement;
    fireEvent.change(select, { target: { value: "bp-live" } });
    fireEvent.click(screen.getByRole("button", { name: /provision/i }));
    await waitFor(() => {
      const post = api.mock.calls.find((c) => (c[1] as RequestInit | undefined)?.method === "POST");
      expect(post).toBeTruthy();
      const body = JSON.parse((post![1] as RequestInit).body as string);
      // H7: the key covers EVERY parameter (partner, slug, blueprint, name)
      expect(body.idempotency_key).toBe("p-1:acme-school:bp-live:Acme School");
    });
    // the step machine renders the polled run's steps
    expect(await screen.findByText(/create_tenant|create tenant/i)).toBeTruthy();
  });
});
