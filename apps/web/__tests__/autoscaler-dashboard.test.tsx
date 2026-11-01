import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AutoscalerDashboard } from "@/components/autoscaler-dashboard";

describe("AutoscalerDashboard", () => {
  it("renders scaler", () => {
    const { container } = render(
      <AutoscalerDashboard name="api" current={3} desired={5} minReplicas={1}
        maxReplicas={10} currentCpu={95} targetCpu={70} action="scale_up"
        scaleUps={3} scaleDowns={1} />
    );
    expect(container.textContent).toContain("Autoscaler: api");
    expect(container.textContent).toContain("Scaling Up");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("70%");
    expect(container.textContent).toContain("1–10");
  });
});
