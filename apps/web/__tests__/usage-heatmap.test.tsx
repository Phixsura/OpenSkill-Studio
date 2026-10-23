import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageHeatmap } from "@/components/usage-heatmap";

describe("UsageHeatmap", () => {
  const cells = Array.from({ length: 168 }, (_, i) => ({
    day: Math.floor(i / 24), hour: i % 24, count: i % 5, intensity: (i % 5) * 20,
  }));
  it("renders heatmap grid", () => {
    const { container } = render(
      <UsageHeatmap cells={cells} totalEvents={500} peakHour={14} peakDay={1} />
    );
    expect(container.textContent).toContain("Usage Heatmap");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("Mon");
    expect(container.textContent).toContain("Sun");
  });
});
