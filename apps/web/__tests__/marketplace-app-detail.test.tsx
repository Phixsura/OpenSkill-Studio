import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ appId: "app-pub-1" }),
  useRouter: () => ({ push: vi.fn() }),
}));

import MarketplaceAppDetailPage from "@/app/(public)/marketplace/apps/[appId]/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("MarketplaceAppDetailPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<MarketplaceAppDetailPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has page structure", () => {
    const { container } = render(<MarketplaceAppDetailPage />, { wrapper: makeWrapper() });
    expect(container.querySelectorAll("div").length).toBeGreaterThan(0);
  });
});
