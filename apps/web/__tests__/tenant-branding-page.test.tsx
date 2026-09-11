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

import TenantBrandingPage from "@/app/(dashboard)/dashboard/tenant/[tenantId]/branding/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

describe("TenantBrandingPage (R394 — token editing + null semantics)", () => {
  beforeEach(() => api.mockReset());

  it("clearing a theme token DELETES the key (never sends an empty string) and empty text fields go null", async () => {
    api.mockImplementation((rawPath: unknown, init?: RequestInit) => {
      const path = String(rawPath ?? "");
      if (path === "/tenants/t-1/branding" && (!init || !init.method))
        return Promise.resolve({
          data: {
            product_display_name: "Acme Academy",
            logo_key: null,
            favicon_key: null,
            theme_tokens: { primary: "#112233", accent: "#445566" },
            login_tagline: "Old tagline",
            email_from_name: null,
            email_footer: null,
            certificate_footer: null,
            support_email: null,
            support_url: null,
            legal_links: [],
          },
        });
      return Promise.resolve({ data: {} });
    });
    render(<TenantBrandingPage />, { wrapper: wrapper() });
    const primary = (await screen.findAllByDisplayValue("#112233"))[1] as HTMLInputElement; // the TEXT twin (color inputs coerce "" to #000000)
    fireEvent.change(primary, { target: { value: "" } }); // clear primary
    const tagline = (await screen.findByDisplayValue("Old tagline")) as HTMLInputElement;
    fireEvent.change(tagline, { target: { value: "" } }); // clear tagline
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      const put = api.mock.calls.find((c) => (c[1] as RequestInit | undefined)?.method === "PUT");
      expect(put).toBeTruthy();
      const body = JSON.parse((put![1] as RequestInit).body as string);
      expect(body.theme_tokens).toEqual({ accent: "#445566" }); // key deleted
      expect("primary" in body.theme_tokens).toBe(false); // never ""
      expect(body.login_tagline).toBeNull(); // "" → null
      expect(body.product_display_name).toBe("Acme Academy");
    });
  });
});
