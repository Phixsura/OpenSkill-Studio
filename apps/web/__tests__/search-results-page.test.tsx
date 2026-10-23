import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchResultsPage } from "@/components/search-results-page";

describe("SearchResultsPage", () => {
  const results = [{ id: "a1", name: "Editor", icon: "📝", tagline: "Code editor",
    category: "tools", rating: 4.5, downloads: 5000, verified: true }];
  it("renders results", () => {
    const { container } = render(
      <SearchResultsPage query="code" results={results} total={1} sortBy="relevance"
        categories={{ tools: 1 }} hasResults={true}
        onSort={vi.fn()} onFilterCategory={vi.fn()} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("code");
    expect(container.textContent).toContain("Editor");
    expect(container.textContent).toContain("1 results");
    expect(container.textContent).toContain("tools");
  });
});
