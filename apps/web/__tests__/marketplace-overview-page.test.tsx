import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceOverviewPage } from "@/components/marketplace-overview-page";

const SECTIONS = [{ title: "Featured", type: "featured", count: 6 }, { title: "Trending", type: "trending", count: 10 }];

describe("MarketplaceOverviewPage", () => {
  it("shows title", () => {
    const { container } = render(<MarketplaceOverviewPage sections={SECTIONS} totalApps={100} totalDevelopers={20} />);
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("100 apps");
  });
  it("shows sections", () => {
    const { container } = render(<MarketplaceOverviewPage sections={SECTIONS} totalApps={0} totalDevelopers={0} />);
    expect(container.textContent).toContain("Featured");
    expect(container.textContent).toContain("Trending");
  });
});
