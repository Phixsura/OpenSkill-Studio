import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceSearchPage } from "@/components/marketplace-search-page";

describe("MarketplaceSearchPage", () => {
  const results = [{ id: "a1", name: "Auth SDK", category: "security", rating: 4.5 }];
  const facets = { categories: { security: 2, design: 1 } };
  it("renders", () => {
    const { container } = render(
      <MarketplaceSearchPage results={results} total={2} query="auth" facets={facets}
        page={1} totalPages={1} onSearch={vi.fn()} onFilter={vi.fn()}
        onAppClick={vi.fn()} onPage={vi.fn()} />
    );
    expect(container.textContent).toContain('2 results for "auth"');
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("⭐ 4.5");
    expect(container.textContent).toContain("security (2)");
  });
});
