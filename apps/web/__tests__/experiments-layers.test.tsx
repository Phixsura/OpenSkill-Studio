import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children, ...rest }: { href: string; children: ReactNode }) => (
    <a href={href} {...rest}>
      {children}
    </a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/experiments/layers",
}));
vi.mock("@/lib/use-me", () => ({ usePlatformAdmin: () => true }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import LayersPage from "@/app/(dashboard)/dashboard/experiments/layers/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const LAYER = {
  id: "L".repeat(26),
  key: "learning-core",
  domain: "learning",
  total_slices: 10000,
  created_at: "2026-10-01T00:00:00Z",
};

beforeEach(() => vi.clearAllMocks());

describe("Layers page (ADR-017 Part L, round 97 A/A probe)", () => {
  it("runs the A/A probe and renders the healthy verdict", async () => {
    api.mockImplementation((async (rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path.endsWith("/aa-probe"))
        return { data: { chi2: 7.12, p: 0.625, healthy: true, n: 2000 } };
      return { data: [LAYER] };
    }) as never);
    render(<LayersPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("A/A probe"));
    const line = await screen.findByTestId("aa-probe-result");
    expect(line.textContent).toContain("p = 0.6250");
    expect(line.textContent).toContain("hash healthy");
  });

  it("flags a suspect hash distribution", async () => {
    api.mockImplementation((async (rawPath: unknown) => {
      const path = String(rawPath ?? "");
      if (path.endsWith("/aa-probe"))
        return { data: { chi2: 99.9, p: 0.0001, healthy: false, n: 2000 } };
      return { data: [LAYER] };
    }) as never);
    render(<LayersPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("A/A probe"));
    expect((await screen.findByTestId("aa-probe-result")).textContent).toContain("SUSPECT");
  });
});
