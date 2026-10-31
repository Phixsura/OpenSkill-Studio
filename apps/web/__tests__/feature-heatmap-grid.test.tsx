import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureHeatmapGrid } from "@/components/feature-heatmap-grid";

describe("FeatureHeatmapGrid", () => {
  it("renders heatmap", () => {
    const hours = new Array(24).fill(0);
    hours[9] = 5; hours[10] = 8;
    const { container } = render(
      <FeatureHeatmapGrid totalEvents={100} peakHourDisplay="10:00" features={[
        { feature: "search", hours, total: 13, peakHour: 10 },
      ]} />
    );
    expect(container.textContent).toContain("Feature Heatmap");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("Peak: 10:00");
    expect(container.textContent).toContain("search");
    expect(container.textContent).toContain("13");
  });
});
