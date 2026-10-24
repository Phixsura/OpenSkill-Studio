import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceSearch } from "@/components/marketplace-search";

describe("MarketplaceSearch", () => {
  const results = [{ name: "Code Editor", description: "A code editor", category: "tools", downloads: 5000, rating: 4.5 }];
  it("renders search", () => {
    const { container } = render(
      <MarketplaceSearch results={results} total={1} query="code" facets={{}}
        sortOptions={["relevance", "downloads"]} onSearch={vi.fn()} onSort={vi.fn()} />
    );
    expect(container.textContent).toContain("Code Editor");
    expect(container.textContent).toContain("1 results");
    expect(container.textContent).toContain("5,000");
  });
});
