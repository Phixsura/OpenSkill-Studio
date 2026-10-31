import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeaturedAppsSection } from "@/components/featured-apps-section";

describe("FeaturedAppsSection", () => {
  it("renders hero and grid", () => {
    const { container } = render(
      <FeaturedAppsSection title="Featured" hero={{ id: "h1", name: "Hero App" }}
        grid={[{ id: "g1", name: "Grid App", featured_reason: "trending" }]} rest={[{ id: "r1", name: "Rest" }]} />
    );
    expect(container.textContent).toContain("Hero App");
    expect(container.textContent).toContain("Grid App");
    expect(container.textContent).toContain("Trending");
    expect(container.textContent).toContain("Rest");
  });
  it("no hero", () => {
    const { container } = render(<FeaturedAppsSection title="Featured" hero={null} grid={[]} rest={[]} />);
    expect(container.textContent).toContain("Featured");
  });
});
