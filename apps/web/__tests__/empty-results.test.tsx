import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmptyResults } from "@/components/empty-results";

describe("EmptyResults", () => {
  it("shows query", () => {
    const { container } = render(<EmptyResults query="test search" />);
    expect(container.textContent).toContain("test search");
  });
  it("shows generic message", () => {
    const { container } = render(<EmptyResults />);
    expect(container.textContent).toContain("No results found");
  });
  it("shows suggestion", () => {
    const { container } = render(<EmptyResults suggestion="Try broader terms" />);
    expect(container.textContent).toContain("broader terms");
  });
});
