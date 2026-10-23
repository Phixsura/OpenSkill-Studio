import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchResultsPage } from "@/components/search-results-page";

describe("SearchResultsPage", () => {
  it("renders results", () => {
    const { container } = render(
      <SearchResultsPage query="slack" results={[{ name: "Slack Bot", description: "A bot" }]}
        total={1} page={1} totalPages={1} facets={{ categories: { comm: 1 } }} onPageChange={vi.fn()} />
    );
    expect(container.textContent).toContain('Search: "slack"');
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("comm (1)");
  });
  it("pagination", () => {
    const fn = vi.fn();
    const { container } = render(
      <SearchResultsPage query="app" results={[]} total={50} page={1} totalPages={3}
        facets={{ categories: {} }} onPageChange={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "→")!);
    expect(fn).toHaveBeenCalledWith(2);
  });
});
