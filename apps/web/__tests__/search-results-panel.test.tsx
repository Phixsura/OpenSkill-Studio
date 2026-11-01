import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SearchResultsPanel } from "@/components/search-results-panel";

describe("SearchResultsPanel", () => {
  it("renders results", () => {
    const { container } = render(
      <SearchResultsPanel query="build" totalDocs={50}
        results={[
          { id: "d1", title: "Getting Started", score: 1.0, type: "docs" },
          { id: "d2", title: "Build Guide", score: 0.8, type: "tutorial" },
        ]} />
    );
    expect(container.textContent).toContain("Search Results");
    expect(container.textContent).toContain("2 results");
    expect(container.textContent).toContain("50 indexed");
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("100% match");
  });
});
