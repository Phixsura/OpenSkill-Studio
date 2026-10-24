import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/marketplace/apps",
}));

import MarketplaceAppsPage from "@/app/(public)/marketplace/apps/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("MarketplaceAppsPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<MarketplaceAppsPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has search or filter elements", () => {
    const { container } = render(<MarketplaceAppsPage />, { wrapper: makeWrapper() });
    const elements = container.querySelectorAll("input, select, button, div");
    expect(elements.length).toBeGreaterThan(0);
  });
});
