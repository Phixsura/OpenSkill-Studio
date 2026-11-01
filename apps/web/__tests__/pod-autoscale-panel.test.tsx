import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PodAutoscalePanel } from "@/components/pod-autoscale-panel";
describe("PodAutoscalePanel", () => {
  it("renders", () => {
    const { container } = render(
      <PodAutoscalePanel currentPods={3} desiredPods={6} action="scale_up"
        metricValue={90} target={50} minPods={1} maxPods={20} />
    );
    expect(container.textContent).toContain("Pod Autoscaler");
    expect(container.textContent).toContain("scale up");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("6");
    expect(container.textContent).toContain("90/50");
    expect(container.textContent).toContain("1-20");
  });
});
