import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DocsSearchResults } from "@/components/docs-search-results";

describe("DocsSearchResults", () => {
  const results = [
    { title: "Authentication", path: "/docs/auth", snippet: "Use API keys to authenticate", score: 5 },
  ];
  it("renders results", () => {
    const { container } = render(<DocsSearchResults results={results} query="API" total={1} />);
    expect(container.textContent).toContain("Authentication");
    expect(container.textContent).toContain("/docs/auth");
    expect(container.textContent).toContain("1 result");
  });
  it("empty state", () => {
    const { container } = render(<DocsSearchResults results={[]} query="xyz" total={0} />);
    expect(container.textContent).toContain("No docs found");
  });
});
