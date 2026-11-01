import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostAnomalyChart } from "@/components/cost-anomaly-chart";

describe("CostAnomalyChart", () => {
  it("renders alert", () => {
    const { container } = render(
      <CostAnomalyChart mean={100} std={5} upperBound={110} status="alert"
        projectedTotal={3000}
        anomalies={[{ day: 4, cost: 500, deviation: 80 }]} />
    );
    expect(container.textContent).toContain("Cost Anomaly Detection");
    expect(container.textContent).toContain("1 anomalies");
    expect(container.textContent).toContain("$100");
    expect(container.textContent).toContain("$110");
    expect(container.textContent).toContain("$3,000");
    expect(container.textContent).toContain("Day 4");
    expect(container.textContent).toContain("$500");
  });
});
