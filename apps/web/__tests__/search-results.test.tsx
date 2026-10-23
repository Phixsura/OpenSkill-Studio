import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SearchResults } from "@/components/search-results";

describe("SearchResults", () => {
  const results = [
    { id: "1", title: "Python SDK", snippet: "Build apps with Python", score: 3, tags: ["sdk"] },
  ];
  it("renders results", () => {
    const { container } = render(<SearchResults results={results} query="Python" total={1} />);
    expect(container.textContent).toContain("Python SDK");
    expect(container.textContent).toContain("Build apps");
    expect(container.textContent).toContain("sdk");
    expect(container.textContent).toContain("1 result");
  });
  it("shows empty", () => {
    const { container } = render(<SearchResults results={[]} query="nope" total={0} />);
    expect(container.textContent).toContain("No results");
  });
});
