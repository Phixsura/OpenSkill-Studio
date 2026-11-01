import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-anomaly-score-card";

describe("RequestAnomalyScoreCard", () => {
  it("shows anomalies", () => {
    const anomalies = [{ request_id: "r1", consumer_id: "c1", anomaly_score: 0.85, severity: "high", top_factor: "latency" }];
    const { container } = render(<Card anomalies={anomalies} totalAnomalies={5} appName="App" />);
    expect(container.textContent).toContain("Anomaly Scores");
    expect(container.textContent).toContain("5 detected");
    expect(container.textContent).toContain("85%");
  });
  it("shows empty", () => {
    const { container } = render(<Card anomalies={[]} totalAnomalies={0} appName="App" />);
    expect(container.textContent).toContain("No anomalies");
  });
});
