import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InstallAnalyticsChart } from "@/components/install-analytics-chart";

const mockStats = { activeInstalls: 1500, totalInstalls: 2000, totalUninstalls: 500, updates: 800, retentionRate: 75.0, churnRate: 25.0 };
const mockSources = [{ source: "marketplace", count: 1200 }, { source: "cli", count: 500 }];
const mockRegions = [{ region: "US", count: 800 }, { region: "EU", count: 600 }];
const mockVersions = [{ version: "2.0.0", count: 900 }, { version: "1.5.0", count: 400 }];

describe("InstallAnalyticsChart", () => {
  it("renders stats cards", () => {
    const { container } = render(
      <InstallAnalyticsChart stats={mockStats} sources={mockSources} regions={mockRegions}
        versions={mockVersions} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("25%");
  });

  it("shows sources tab", () => {
    const { getByText, container } = render(
      <InstallAnalyticsChart stats={mockStats} sources={mockSources} regions={mockRegions}
        versions={mockVersions} extensionName="MyExt" />
    );
    fireEvent.click(getByText("Sources"));
    expect(container.textContent).toContain("marketplace");
    expect(container.textContent).toContain("1200");
  });

  it("shows versions tab", () => {
    const { getByText, container } = render(
      <InstallAnalyticsChart stats={mockStats} sources={mockSources} regions={mockRegions}
        versions={mockVersions} extensionName="MyExt" />
    );
    fireEvent.click(getByText("Versions"));
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("900 users");
  });
});
