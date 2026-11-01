import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SearchResultsHeader } from "@/components/search-results-header";

describe("SearchResultsHeader", () => {
  it("shows results", () => {
    const { container } = render(<SearchResultsHeader query="lms" total={5} page={1} totalPages={1} suggestion={null} />);
    expect(container.textContent).toContain('Results for "lms"');
    expect(container.textContent).toContain("5 results");
  });
  it("shows no results", () => {
    const { container } = render(<SearchResultsHeader query="xyz" total={0} page={1} totalPages={1} suggestion="Try 'x'" />);
    expect(container.textContent).toContain("No results");
    expect(container.textContent).toContain("Try");
  });
});
