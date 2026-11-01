import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceStatsDashboard } from "@/components/marketplace-stats-dashboard";

const mockStats = {
  totalExtensions: 245, totalConnectors: 58, totalDevelopers: 120,
  totalInstalls: 89000, newThisWeek: 12, avgRating: 4.3,
};
const mockTrending = [
  { id: "1", name: "Slack Bot Pro", author: "alice", category: "messaging", installs: 5200, rating: 4.8, trend: "up" as const },
  { id: "2", name: "Dark Theme Ultra", author: "bob", category: "themes", installs: 4100, rating: 4.6, trend: "new" as const },
];
const mockCategories = [
  { name: "Tools", count: 85 }, { name: "Themes", count: 42 },
  { name: "Connectors", count: 58 }, { name: "Analytics", count: 30 },
];

describe("MarketplaceStatsDashboard", () => {
  it("renders stats cards", () => {
    const { container } = render(
      <MarketplaceStatsDashboard stats={mockStats} trending={mockTrending} categories={mockCategories} />
    );
    expect(container.textContent).toContain("245");
    expect(container.textContent).toContain("89,000");
    expect(container.textContent).toContain("4.3");
  });

  it("renders trending with badges", () => {
    const { container } = render(
      <MarketplaceStatsDashboard stats={mockStats} trending={mockTrending} categories={mockCategories} />
    );
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("NEW");
  });

  it("renders categories with bars", () => {
    const { container } = render(
      <MarketplaceStatsDashboard stats={mockStats} trending={mockTrending} categories={mockCategories} />
    );
    expect(container.textContent).toContain("Tools");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("Analytics");
  });
});
