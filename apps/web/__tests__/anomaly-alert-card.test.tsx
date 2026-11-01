import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnomalyAlertCard } from "@/components/anomaly-alert-card";

describe("AnomalyAlertCard", () => {
  it("renders anomalies", () => {
    const anomalies = [{ index: 6, value: 500, z_score: 3.5, type: "spike", deviation_pct: 400 }];
    const { container } = render(
      <AnomalyAlertCard anomalies={anomalies} mean={100} stdDev={15} anomalyRate={10} />
    );
    expect(container.textContent).toContain("Usage Anomalies");
    expect(container.textContent).toContain("1 detected");
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("z=3.5");
  });
  it("all normal", () => {
    const { container } = render(
      <AnomalyAlertCard anomalies={[]} mean={100} stdDev={5} anomalyRate={0} />
    );
    expect(container.textContent).toContain("All normal");
  });
});
