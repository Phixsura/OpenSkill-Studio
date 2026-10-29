import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiAnomalyDetectorCard from "../src/components/api-developer-api-api-anomaly-detector-card";

const anomalies = [
  { anomaly_id: "a1", endpoint: "/api/users", metric: "traffic", severity: "critical", current_value: 500, baseline_value: 100, deviation_pct: 400 },
];

describe("APIDeveloperAPIApiAnomalyDetectorCard", () => {
  it("shows anomalies", () => {
    const { container } = render(<APIDeveloperAPIApiAnomalyDetectorCard anomalies={anomalies} criticalCount={1} appName="App" />);
    expect(container.textContent).toContain("Anomaly Detector");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("+400%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiAnomalyDetectorCard anomalies={[]} criticalCount={0} appName="App" />);
    expect(container.textContent).toContain("No anomalies detected");
  });
});
