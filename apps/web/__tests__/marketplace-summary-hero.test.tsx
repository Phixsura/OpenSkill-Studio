import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceSummaryHero } from "@/components/marketplace-summary-hero";

const summary = {
  totalExtensions: 500, totalDevelopers: 200, totalInstalls: 50000,
  totalReviews: 12000, avgRating: 4.3, categories: 12, connectors: 45,
};

describe("MarketplaceSummaryHero", () => {
  it("renders summary stats", () => {
    const { container } = render(<MarketplaceSummaryHero summary={summary} />);
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("4.3");
  });
});
