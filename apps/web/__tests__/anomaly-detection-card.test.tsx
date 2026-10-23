import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnomalyDetectionCard } from "@/components/anomaly-detection-card";

describe("AnomalyDetectionCard", () => {
  it("renders normal", () => {
    const { container } = render(
      <AnomalyDetectionCard metricName="CPU" currentValue={50} mean={48} upper={60} lower={36}
        isAnomaly={false} direction="normal" severity="info" />
    );
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("50");
  });
  it("renders anomaly", () => {
    const { container } = render(
      <AnomalyDetectionCard metricName="Latency" currentValue={500} mean={100} upper={150} lower={50}
        isAnomaly={true} direction="above" severity="critical" />
    );
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("above");
  });
});
