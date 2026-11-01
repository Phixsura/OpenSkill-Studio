import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";

import MarketplaceFeaturedPage from "@/app/(public)/marketplace/featured/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("MarketplaceFeaturedPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<MarketplaceFeaturedPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has a heading", () => {
    const { container } = render(<MarketplaceFeaturedPage />, { wrapper: makeWrapper() });
    const h = container.querySelector("h1, h2");
    expect(h).toBeTruthy();
  });
});
