import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";

import MarketplaceCategoriesPage from "@/app/(public)/marketplace/apps/categories/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("MarketplaceCategoriesPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<MarketplaceCategoriesPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has heading", () => {
    const { container } = render(<MarketplaceCategoriesPage />, { wrapper: makeWrapper() });
    const h = container.querySelector("h1, h2");
    expect(h).toBeTruthy();
  });
});
