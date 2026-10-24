import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UtilHeatmap } from "@/components/util-heatmap";

describe("UtilHeatmap", () => {
  it("renders", () => {
    const { container } = render(
      <UtilHeatmap services={["api", "db"]} timeSlots={3} hotspotCount={2} avgUtilization={59}
        data={{ api: [40, 85, 60], db: [30, 50, 90] }} />
    );
    expect(container.textContent).toContain("Utilization Heatmap");
    expect(container.textContent).toContain("avg 59%");
    expect(container.textContent).toContain("2 hotspots");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("90");
  });
});
