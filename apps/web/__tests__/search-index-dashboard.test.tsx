import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SearchIndexDashboard } from "@/components/search-index-dashboard";

describe("SearchIndexDashboard", () => {
  it("renders results", () => {
    const { container } = render(
      <SearchIndexDashboard totalDocuments={100} totalWords={5000} query="web"
        onSearch={vi.fn()} results={[
          { id: "d1", score: 1.0, matchedTerms: ["web"] },
          { id: "d2", score: 0.5, matchedTerms: ["web"] },
        ]} />
    );
    expect(container.textContent).toContain("Search Index");
    expect(container.textContent).toContain("100 docs");
    expect(container.textContent).toContain("5000 words");
    expect(container.textContent).toContain("d1");
    expect(container.textContent).toContain("score: 1");
  });
});
