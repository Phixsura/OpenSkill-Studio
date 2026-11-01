import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictorCard from "../src/components/api-developer-platform-sdk-api-platform-api-consumer-churn-predictor-card";

const predictions = [{ consumer_id: "acme", churn_risk_score: 80, risk_level: "critical", days_since_last_call: 45, api_calls_trend_pct: -75 }];

describe("Card", () => {
  it("shows churn predictions", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictorCard predictions={predictions} atRiskCount={3} appName="App" />);
    expect(container.textContent).toContain("Churn Predictor");
    expect(container.textContent).toContain("3 at risk");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("80");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("45d idle");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerChurnPredictorCard predictions={[]} atRiskCount={0} appName="App" />);
    expect(container.textContent).toContain("No churn predictions");
  });
});
