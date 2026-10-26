import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RevenueDashboard } from "@/components/revenue-dashboard";

const mockMetrics = {
  grossCents: 500000, refundsCents: 25000, netCents: 475000,
  platformFeeCents: 71250, developerCents: 403750, mrr: 150000,
};
const mockTiers = [
  { tier: "pro", revenueCents: 350000 },
  { tier: "basic", revenueCents: 150000 },
];
const mockTop = [
  { extensionId: "ext-1", name: "Slack Bot Pro", revenueCents: 200000 },
  { extensionId: "ext-2", name: "Data Sync", revenueCents: 150000 },
];

describe("RevenueDashboard", () => {
  it("renders revenue metrics", () => {
    const { container } = render(
      <RevenueDashboard metrics={mockMetrics} tiers={mockTiers}
        topExtensions={mockTop} period="October 2024" />
    );
    expect(container.textContent).toContain("$5,000.00");
    expect(container.textContent).toContain("$1,500.00");
  });

  it("shows tier breakdown", () => {
    const { getByText, container } = render(
      <RevenueDashboard metrics={mockMetrics} tiers={mockTiers}
        topExtensions={mockTop} period="Oct" />
    );
    fireEvent.click(getByText("By Tier"));
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("$3,500.00");
  });

  it("shows top extensions", () => {
    const { getByText, container } = render(
      <RevenueDashboard metrics={mockMetrics} tiers={mockTiers}
        topExtensions={mockTop} period="Oct" />
    );
    fireEvent.click(getByText("Top Extensions"));
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("#1");
  });
});
