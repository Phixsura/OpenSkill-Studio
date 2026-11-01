import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActivityHeatmapGrid } from "@/components/activity-heatmap-grid";

describe("ActivityHeatmapGrid", () => {
  it("renders heatmap", () => {
    const grid = [
      { day: "Mon", hours: new Array(24).fill(0), total: 3 },
      { day: "Tue", hours: new Array(24).fill(0), total: 0 },
    ];
    grid[0].hours[9] = 2;
    grid[0].hours[10] = 1;
    const { container } = render(
      <ActivityHeatmapGrid grid={grid} maxValue={3} peakDisplay="Fri 14:00" totalEvents={100} />
    );
    expect(container.textContent).toContain("Activity Heatmap");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("Peak: Fri 14:00");
    expect(container.textContent).toContain("Mon");
    expect(container.textContent).toContain("Tue");
  });
});
