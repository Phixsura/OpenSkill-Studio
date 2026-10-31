import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AutoScaleCard } from "@/components/auto-scale-card";

describe("AutoScaleCard", () => {
  it("renders", () => {
    const { container } = render(
      <AutoScaleCard name="CPU Autoscaler" metric="cpu_pct" targetValue={70}
        currentReplicas={3} desiredReplicas={5} action="scale_up"
        minReplicas={1} maxReplicas={10} />
    );
    expect(container.textContent).toContain("CPU Autoscaler");
    expect(container.textContent).toContain("Scaling Up");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("70%");
    expect(container.textContent).toContain("1-10");
  });
});
