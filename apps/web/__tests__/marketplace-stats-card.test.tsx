import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceStatsCard } from "@/components/marketplace-stats-card";

describe("MarketplaceStatsCard", () => {
  it("shows all stats", () => {
    const { container } = render(<MarketplaceStatsCard totalApps={50} publishedApps={30} totalDevelopers={10} totalInstallations={300} />);
    expect(container.textContent).toContain("30");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("300");
  });

  it("shows labels", () => {
    const { container } = render(<MarketplaceStatsCard totalApps={0} publishedApps={0} totalDevelopers={0} totalInstallations={0} />);
    expect(container.textContent).toContain("Published Apps");
    expect(container.textContent).toContain("Developers");
  });

  it("renders 4 cards", () => {
    const { container } = render(<MarketplaceStatsCard totalApps={1} publishedApps={1} totalDevelopers={1} totalInstallations={1} />);
    expect(container.querySelectorAll("[class*='rounded-lg']").length).toBe(4);
  });
});
