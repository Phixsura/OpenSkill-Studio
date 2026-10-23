import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostAnomalyAlert } from "@/components/cost-anomaly-alert";

describe("CostAnomalyAlert", () => {
  it("renders anomalies", () => {
    const { container } = render(
      <CostAnomalyAlert mean={100} std={5} hasAnomaly={true} potentialSavings="$400.00"
        anomalies={[{ day: 5, cost: 500, zScore: 80, direction: "spike" }]} />
    );
    expect(container.textContent).toContain("Cost Anomalies");
    expect(container.textContent).toContain("1 detected");
    expect(container.textContent).toContain("Day 5");
    expect(container.textContent).toContain("$500");
    expect(container.textContent).toContain("$400.00");
  });
});
