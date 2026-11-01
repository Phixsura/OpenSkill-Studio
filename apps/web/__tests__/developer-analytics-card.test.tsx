import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperAnalyticsCard } from "@/components/developer-analytics-card";

const stats = {
  developerId: "dev-1", totalExtensions: 5, totalInstalls: 12000,
  totalReviews: 340, avgRating: 4.7, totalRevenueCents: 150000,
  activeUsers30d: 3200, topExtension: "Auth Plugin",
};

describe("DeveloperAnalyticsCard", () => {
  it("renders stats", () => {
    const { container } = render(<DeveloperAnalyticsCard stats={stats} />);
    expect(container.textContent).toContain("12,000");
    expect(container.textContent).toContain("4.7/5");
    expect(container.textContent).toContain("$1,500.00");
    expect(container.textContent).toContain("Auth Plugin");
  });
});
