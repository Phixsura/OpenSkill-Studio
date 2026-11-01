import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionInsightsPanel } from "@/components/extension-insights-panel";

const mockMetrics = [
  { label: "Installs", current: 1200, previous: 800, unit: "" },
  { label: "API Calls", current: 45000, previous: 50000, unit: "" },
  { label: "Avg Latency", current: 42, previous: 55, unit: "ms" },
  { label: "Revenue", current: 4999, previous: 3200, unit: "¢" },
];

const mockEvents = [
  { name: "api.call", count: 25000, trend: "up" as const },
  { name: "config.read", count: 8000, trend: "stable" as const },
  { name: "webhook.send", count: 3500, trend: "down" as const },
];

describe("ExtensionInsightsPanel", () => {
  it("renders metrics with deltas", () => {
    const { container } = render(
      <ExtensionInsightsPanel extensionName="Slack Bot" period="Last 7 days"
        metrics={mockMetrics} topEvents={mockEvents} healthScore={95} />
    );
    expect(container.textContent).toContain("Slack Bot Insights");
    expect(container.textContent).toContain("1,200");
    expect(container.textContent).toContain("+50.0%"); // 1200 vs 800
    expect(container.textContent).toContain("-10.0%"); // 45000 vs 50000
  });

  it("renders health score", () => {
    const { container } = render(
      <ExtensionInsightsPanel extensionName="Test" period="7d"
        metrics={mockMetrics} topEvents={mockEvents} healthScore={95} />
    );
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("Health");
  });

  it("renders top events with trends", () => {
    const { container } = render(
      <ExtensionInsightsPanel extensionName="Test" period="7d"
        metrics={mockMetrics} topEvents={mockEvents} healthScore={80} />
    );
    expect(container.textContent).toContain("api.call");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("↑");
    expect(container.textContent).toContain("↓");
  });
});
