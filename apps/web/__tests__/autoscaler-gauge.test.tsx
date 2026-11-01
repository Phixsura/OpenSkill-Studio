import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AutoscalerGauge } from "@/components/autoscaler-gauge";

describe("AutoscalerGauge", () => {
  it("renders scale up", () => {
    const { container } = render(
      <AutoscalerGauge currentReplicas={3} targetReplicas={5} action="scale_up"
        currentCpuPct={90} targetCpuPct={70} min={2} max={20} />
    );
    expect(container.textContent).toContain("Autoscaler");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("scale up");
    expect(container.textContent).toContain("CPU: 90%");
    expect(container.textContent).toContain("2–20 pods");
  });
});
