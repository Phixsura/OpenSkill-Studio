import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceAdminDashboard } from "@/components/marketplace-admin-dashboard";

const mockStats = {
  totalExtensions: 245, pendingReviews: 12, activeConnectors: 58,
  totalDevelopers: 120, totalRevenue: 4599900, openIncidents: 2,
  flaggedReviews: 5, suspendedExtensions: 1,
};

const mockAlerts = [
  { id: "a1", severity: "critical" as const, message: "Security scan failed for ext-42", timestamp: "5m ago", resolved: false },
  { id: "a2", severity: "warning" as const, message: "High error rate on Slack connector", timestamp: "1h ago", resolved: false },
  { id: "a3", severity: "info" as const, message: "New developer registered", timestamp: "2h ago", resolved: true },
];

describe("MarketplaceAdminDashboard", () => {
  it("renders admin stats", () => {
    const { container } = render(
      <MarketplaceAdminDashboard stats={mockStats} alerts={mockAlerts} />
    );
    expect(container.textContent).toContain("Marketplace Admin");
    expect(container.textContent).toContain("245");
    expect(container.textContent).toContain("$45,999");
    expect(container.textContent).toContain("120");
  });

  it("shows unresolved alerts only", () => {
    const { container } = render(
      <MarketplaceAdminDashboard stats={mockStats} alerts={mockAlerts} />
    );
    expect(container.textContent).toContain("Active Alerts (2)");
    expect(container.textContent).toContain("Security scan failed");
    expect(container.textContent).not.toContain("New developer registered");
  });

  it("calls onResolveAlert", () => {
    const onResolve = vi.fn();
    const { getAllByText } = render(
      <MarketplaceAdminDashboard stats={mockStats} alerts={mockAlerts} onResolveAlert={onResolve} />
    );
    fireEvent.click(getAllByText("Resolve")[0]);
    expect(onResolve).toHaveBeenCalledWith("a1");
  });
});
