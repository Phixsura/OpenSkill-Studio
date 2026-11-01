import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceHomepageLayout } from "@/components/marketplace-homepage-layout";

describe("MarketplaceHomepageLayout", () => {
  it("renders sections", () => {
    const sections = [
      { key: "hero", title: "Featured", type: "hero_carousel" },
      { key: "trending", title: "Trending", type: "app_row" },
    ];
    const { container } = render(
      <MarketplaceHomepageLayout sections={sections} statsBar={{ apps: 500, developers: 100, installs: 25000 }} personalized={false} />
    );
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("Featured");
    expect(container.textContent).toContain("Trending");
  });
  it("shows personalized", () => {
    const { container } = render(
      <MarketplaceHomepageLayout sections={[]} statsBar={{ apps: 0, developers: 0, installs: 0 }} personalized={true} />
    );
    expect(container.textContent).toContain("Personalized for you");
  });
});
