import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostAnomalyAlert } from "@/components/cost-anomaly-alert";

describe("CostAnomalyAlert", () => {
  it("renders anomalies", () => {
    const { container } = render(
      <CostAnomalyAlert meanDaily={131} totalDisplay="$655.00" hasAnomalies={true}
        anomalies={[{ date: "2026-10-23", amount: 250, expected: 131,
          deviationPct: 90.8, service: "compute", display: "$250.00 (+91%)" }]} />
    );
    expect(container.textContent).toContain("Cost Anomalies");
    expect(container.textContent).toContain("1 spikes");
    expect(container.textContent).toContain("2026-10-23");
    expect(container.textContent).toContain("$250.00 (+91%)");
    expect(container.textContent).toContain("$655.00");
  });
});
