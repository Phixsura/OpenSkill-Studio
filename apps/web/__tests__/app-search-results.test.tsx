import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppSearchResults } from "@/components/app-search-results";

const RESULTS = [
  { id: "1", name: "App One", slug: "app-one", description: "First app", category: "connector", installCount: 42 },
  { id: "2", name: "App Two", slug: "app-two", description: null, category: "automation", installCount: 10 },
];

describe("AppSearchResults", () => {
  it("shows results", () => {
    const { container } = render(<AppSearchResults results={RESULTS} />);
    expect(container.textContent).toContain("App One");
    expect(container.textContent).toContain("App Two");
  });

  it("shows result count", () => {
    const { container } = render(<AppSearchResults results={RESULTS} query="test" />);
    expect(container.textContent).toContain("2 results");
  });

  it("shows loading", () => {
    const { container } = render(<AppSearchResults results={[]} loading />);
    expect(container.textContent).toContain("Searching");
  });

  it("shows no results", () => {
    const { container } = render(<AppSearchResults results={[]} query="xyz" />);
    expect(container.textContent).toContain("No apps found");
  });

  it("shows install count", () => {
    const { container } = render(<AppSearchResults results={RESULTS} />);
    expect(container.textContent).toContain("42");
  });
});
