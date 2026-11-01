import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperPortalDashboard } from "@/components/developer-portal-dashboard";

const mockStats = {
  extensionsPublished: 5,
  totalDownloads: 12500,
  activeInstalls: 3200,
  avgRating: 4.6,
  apiCallsToday: 8500,
  apiQuotaUsed: 85,
  webhookDeliveries: 142,
  webhookFailures: 3,
};

const mockActivities = [
  { id: "1", type: "install" as const, message: "Slack Connector installed by Org A", timestamp: "2m ago" },
  { id: "2", type: "review" as const, message: "New review on Code Formatter", timestamp: "1h ago" },
  { id: "3", type: "webhook" as const, message: "Webhook delivered to hooks.example.com", timestamp: "3h ago" },
];

describe("DeveloperPortalDashboard", () => {
  it("renders stats cards", () => {
    const { container } = render(
      <DeveloperPortalDashboard stats={mockStats} activities={mockActivities} />
    );
    expect(container.textContent).toContain("Developer Portal");
    expect(container.textContent).toContain("12,500");
    expect(container.textContent).toContain("4.6");
    expect(container.textContent).toContain("3,200");
  });

  it("renders API usage and webhooks", () => {
    const { container } = render(
      <DeveloperPortalDashboard stats={mockStats} activities={mockActivities} />
    );
    expect(container.textContent).toContain("8,500");
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("142");
    expect(container.textContent).toContain("Delivered");
  });

  it("renders recent activity", () => {
    const { container } = render(
      <DeveloperPortalDashboard stats={mockStats} activities={mockActivities} />
    );
    expect(container.textContent).toContain("Slack Connector");
    expect(container.textContent).toContain("Code Formatter");
    expect(container.textContent).toContain("install");
    expect(container.textContent).toContain("review");
  });
});
