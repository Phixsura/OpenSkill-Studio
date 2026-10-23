import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnomalyChart } from "@/components/anomaly-chart";

describe("AnomalyChart", () => {
  it("renders anomalies", () => {
    const { container } = render(
      <AnomalyChart mean={15} std={12} totalPoints={10} anomalyRate={10}
        anomalies={[{ index: 6, label: "sun_spike", value: 50, zScore: 3.2, direction: "high" }]} />
    );
    expect(container.textContent).toContain("Anomaly Detection");
    expect(container.textContent).toContain("1 anomalies");
    expect(container.textContent).toContain("sun_spike");
    expect(container.textContent).toContain("z=3.2");
    expect(container.textContent).toContain("50");
  });
});
