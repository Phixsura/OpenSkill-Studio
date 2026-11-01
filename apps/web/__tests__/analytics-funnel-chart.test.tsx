import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalyticsFunnelChart } from "@/components/analytics-funnel-chart";

const mockStages = [
  { name: "discovery", count: 1000, conversionRate: 100 },
  { name: "view", count: 600, conversionRate: 60, dropOff: 40 },
  { name: "install", count: 200, conversionRate: 20, dropOff: 66.7 },
  { name: "activate", count: 150, conversionRate: 15, dropOff: 25 },
  { name: "retain", count: 80, conversionRate: 8, dropOff: 46.7 },
];

const mockSources = [
  { source: "search", stages: { discovery: 500, view: 300, install: 100 } },
  { source: "browse", stages: { discovery: 300, view: 200, install: 80 } },
];

describe("AnalyticsFunnelChart", () => {
  it("renders funnel stages", () => {
    const { container } = render(
      <AnalyticsFunnelChart stages={mockStages} sources={mockSources}
        extensionName="MyExt" totalUsers={1000} />
    );
    expect(container.textContent).toContain("discovery");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("↓40%");
  });

  it("shows total users", () => {
    const { container } = render(
      <AnalyticsFunnelChart stages={mockStages} sources={mockSources}
        extensionName="MyExt" totalUsers={1000} />
    );
    expect(container.textContent).toContain("1000 total users");
  });

  it("switches to sources view", () => {
    const { getByText, container } = render(
      <AnalyticsFunnelChart stages={mockStages} sources={mockSources}
        extensionName="MyExt" totalUsers={1000} />
    );
    fireEvent.click(getByText("Sources"));
    expect(container.textContent).toContain("search");
    expect(container.textContent).toContain("browse");
  });
});
