import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageHeatmap } from "@/components/usage-heatmap";

describe("UsageHeatmap", () => {
  it("renders grid", () => {
    const rows = [
      { day: "Mon", hours: Array(24).fill(5), total: 120 },
      { day: "Tue", hours: Array(24).fill(3), total: 72 },
    ];
    const { container } = render(<UsageHeatmap rows={rows} peakHour={14} />);
    expect(container.textContent).toContain("Mon");
    expect(container.textContent).toContain("Peak: 14:00");
  });
});
