import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceStatsOverview } from "@/components/marketplace-stats-overview";

describe("MarketplaceStatsOverview", () => {
  it("renders stats", () => {
    const { container } = render(
      <MarketplaceStatsOverview appsDisplay="500" devsDisplay="200"
        installsDisplay="2,500,000" apiDisplay="50,000,000"
        ratingDisplay="4.3 ⭐" reviewsDisplay="15,000"
        categories={8} growthDisplay="+35 this month" health="thriving" />
    );
    expect(container.textContent).toContain("Marketplace Stats");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("2,500,000");
    expect(container.textContent).toContain("4.3 ⭐");
    expect(container.textContent).toContain("+35 this month");
    expect(container.textContent).toContain("thriving");
    expect(container.textContent).toContain("8 categories");
  });
});
