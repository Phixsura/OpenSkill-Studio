import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PodScalerSim } from "@/components/pod-scaler-sim";

describe("PodScalerSim", () => {
  it("renders scaler", () => {
    const { container } = render(
      <PodScalerSim currentPods={3} desiredPods={6} currentCpu={90} targetCpu={50}
        action="scale_up" atMin={false} atMax={false} minPods={1} maxPods={20} />
    );
    expect(container.textContent).toContain("Pod Autoscaler");
    expect(container.textContent).toContain("Scaling Up");
    expect(container.textContent).toContain("3 pods");
    expect(container.textContent).toContain("6 pods");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("1–20");
  });
});
