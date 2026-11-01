import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UtilHeatmap } from "@/components/util-heatmap";
describe("UtilHeatmap", () => {
  it("renders", () => {
    const { container } = render(
      <UtilHeatmap hotNodes={1} avgCpu={60}
        cells={[
          { node: "n1", cpuPct: 30, memoryPct: 40, color: "green" },
          { node: "n2", cpuPct: 90, memoryPct: 85, color: "red" },
        ]} />
    );
    expect(container.textContent).toContain("Utilization Heatmap");
    expect(container.textContent).toContain("1 hot");
    expect(container.textContent).toContain("avg 60% CPU");
  });
});
