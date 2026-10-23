import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SearchAnalyticsDashboard } from "@/components/search-analytics-dashboard";

describe("SearchAnalyticsDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <SearchAnalyticsDashboard totalSearches={1000} uniqueQueries={250}
        topQueries={[{ query: "auth sdk", count: 50 }, { query: "payment", count: 30 }]}
        zeroResultQueries={["foo bar"]} zeroResultRate={5} clickThroughRate={35} />
    );
    expect(container.textContent).toContain("Search Analytics");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("35%");
    expect(container.textContent).toContain("auth sdk");
    expect(container.textContent).toContain("foo bar");
  });
});
