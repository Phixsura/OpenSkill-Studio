import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SearchResultsRanked } from "@/components/search-results-ranked";

describe("SearchResultsRanked", () => {
  it("renders results", () => {
    const { container } = render(
      <SearchResultsRanked query="slack" results={[
        { name: "Slack Bot", description: "Integrate", installs: 50000, rating: 4.5, score: 95.2 },
        { name: "Slack Notifier", description: "Notify", installs: 1000, rating: 4.0, score: 72.1 },
      ]} />
    );
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("2 apps found");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("4.5");
  });
});
