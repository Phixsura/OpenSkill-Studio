import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureUsageHeatmap } from "@/components/feature-usage-heatmap";

describe("FeatureUsageHeatmap", () => {
  const features = [
    { feature: "Search", category: "core", total_usage: 970, avg_daily: 138.6, intensity_pct: 100, trend: "up" },
    { feature: "Export", category: "tools", total_usage: 67, avg_daily: 9.6, intensity_pct: 6.9, trend: "down" },
  ];
  it("renders", () => {
    const { container } = render(<FeatureUsageHeatmap features={features} periodDays={7} />);
    expect(container.textContent).toContain("Feature Usage");
    expect(container.textContent).toContain("Last 7 days");
    expect(container.textContent).toContain("Search");
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("970");
    expect(container.textContent).toContain("Export");
    expect(container.textContent).toContain("📉");
  });
});
