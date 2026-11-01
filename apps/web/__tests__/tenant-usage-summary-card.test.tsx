import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TenantUsageSummaryCard from "../src/components/tenant-usage-summary-card";

const metrics = [
  { metric: "api_calls", current: 8000, limit: 10000, usage_pct: 80, growth_pct: 33.3 },
  { metric: "storage_mb", current: 400, limit: 500, usage_pct: 80, growth_pct: 14.3 },
];

describe("TenantUsageSummaryCard", () => {
  it("renders header", () => {
    const { container } = render(
      <TenantUsageSummaryCard
        metrics={metrics}
        health="warning"
        totalCostDollars={25}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("Usage Summary");
  });

  it("shows health badge", () => {
    const { container } = render(
      <TenantUsageSummaryCard
        metrics={metrics}
        health="warning"
        totalCostDollars={0}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Warning");
  });

  it("shows cost", () => {
    const { container } = render(
      <TenantUsageSummaryCard
        metrics={metrics}
        health="healthy"
        totalCostDollars={25}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("$25.00");
  });

  it("renders metrics with bars", () => {
    const { container } = render(
      <TenantUsageSummaryCard
        metrics={metrics}
        health="healthy"
        totalCostDollars={0}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("8.0K/10.0K");
  });

  it("shows growth indicators", () => {
    const { container } = render(
      <TenantUsageSummaryCard
        metrics={metrics}
        health="healthy"
        totalCostDollars={0}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("↑33.3%");
  });

  it("shows empty state", () => {
    const { container } = render(
      <TenantUsageSummaryCard metrics={[]} health="healthy" totalCostDollars={0} appName="App" />,
    );
    expect(container.textContent).toContain("No usage data");
  });
});
