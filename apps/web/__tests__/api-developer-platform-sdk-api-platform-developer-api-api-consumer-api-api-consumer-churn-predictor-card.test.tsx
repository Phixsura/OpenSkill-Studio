import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-churn-predictor-card";

describe("ConsumerChurnPredictorCard", () => {
  it("shows predictions", () => {
    const predictions = [{ consumer_id: "c1", churn_risk_pct: 65, risk_level: "high", top_signal: "usage_decline" }];
    const { container } = render(<Card predictions={predictions} atRiskCount={1} appName="App" />);
    expect(container.textContent).toContain("Churn Predictor");
    expect(container.textContent).toContain("65%");
    expect(container.textContent).toContain("usage_decline");
    expect(container.textContent).toContain("1 at risk");
  });
  it("shows empty", () => {
    const { container } = render(<Card predictions={[]} atRiskCount={0} appName="App" />);
    expect(container.textContent).toContain("No predictions");
  });
});
