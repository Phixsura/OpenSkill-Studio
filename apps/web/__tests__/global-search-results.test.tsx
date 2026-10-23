import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GlobalSearchResults } from "@/components/global-search-results";

describe("GlobalSearchResults", () => {
  it("renders results", () => {
    const results = { apps: [{ type: "app", name: "Slack Bot" }], developers: [], docs: [] };
    const { container } = render(<GlobalSearchResults query="slack" results={results} total={1} />);
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain('1 results for "slack"');
  });
  it("empty state", () => {
    const { container } = render(<GlobalSearchResults query="zzz" results={{}} total={0} />);
    expect(container.textContent).toContain("No results");
  });
});
