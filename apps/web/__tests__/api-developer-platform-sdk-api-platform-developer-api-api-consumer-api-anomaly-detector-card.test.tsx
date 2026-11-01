import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-anomaly-detector-card";

describe("AnomalyDetectorCard", () => {
  it("shows anomalies", () => {
    const alerts = [{ alert_id: "a1", consumer_id: "c1", metric: "requests", deviation_pct: 150, severity: "high" }];
    const { container } = render(<Card alerts={alerts} totalAlerts={1} appName="App" />);
    expect(container.textContent).toContain("Anomaly Detector");
    expect(container.textContent).toContain("1 anomalies");
    expect(container.textContent).toContain("150%");
  });
  it("shows no anomalies", () => {
    const { container } = render(<Card alerts={[]} totalAlerts={0} appName="App" />);
    expect(container.textContent).toContain("No anomalies detected");
  });
});
