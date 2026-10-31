import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnomalyDetectionCard } from "@/components/anomaly-detection-card";

describe("AnomalyDetectionCard", () => {
  it("renders", () => {
    const { container } = render(
      <AnomalyDetectionCard metricsChecked={5} hasAnomaly={true}
        anomalies={[{ metric: "cpu", latest: 95, mean: 40, zScore: 27.5, type: "high" }]} />
    );
    expect(container.textContent).toContain("Anomaly Detection");
    expect(container.textContent).toContain("1 anomalies");
    expect(container.textContent).toContain("cpu: 95");
    expect(container.textContent).toContain("mean 40");
  });
});
