import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ActivityHeatmapGrid } from "@/components/activity-heatmap-grid";

describe("ActivityHeatmapGrid", () => {
  const cells = [
    { day: "Mon", hour: 9, count: 10, intensity: 100 },
    { day: "Mon", hour: 10, count: 5, intensity: 50 },
  ];
  const peak = { day: "Mon", hour: 9, count: 10 };
  it("renders", () => {
    const { container } = render(
      <ActivityHeatmapGrid cells={cells} days={["Mon"]} totalEvents={15} peak={peak} />
    );
    expect(container.textContent).toContain("Activity Heatmap");
    expect(container.textContent).toContain("15 events");
    expect(container.textContent).toContain("Peak: Mon at 9:00");
  });
});
