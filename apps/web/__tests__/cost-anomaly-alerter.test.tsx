import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostAnomalyAlerter } from "@/components/cost-anomaly-alerter";

describe("CostAnomalyAlerter", () => {
  it("renders alert", () => {
    const { container } = render(
      <CostAnomalyAlerter anomaly={true} current={500} mean={101} zScore={145}
        type="spike" alert={true} spikes={1} />
    );
    expect(container.textContent).toContain("Cost Alert");
    expect(container.textContent).toContain("Spike!");
    expect(container.textContent).toContain("$500");
    expect(container.textContent).toContain("$101");
    expect(container.textContent).toContain("145");
  });

  it("renders normal", () => {
    const { container } = render(
      <CostAnomalyAlerter anomaly={false} current={103} mean={100} zScore={1.1}
        type="normal" alert={false} spikes={0} />
    );
    expect(container.textContent).toContain("Normal");
  });
});
