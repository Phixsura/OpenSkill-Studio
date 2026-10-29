import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-api-usage-forecast-card";

describe("UsageForecastCard", () => {
  it("shows forecasts", () => {
    const forecasts = [{ consumer_id: "c1", next_period: "2024-07", predicted_requests: 15000, growth_rate_pct: 25.5, confidence: "high", trend: "growing" }];
    const { container } = render(<Card forecasts={forecasts} appName="App" />);
    expect(container.textContent).toContain("Usage Forecast");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("25.5%");
    expect(container.textContent).toContain("15,000 predicted");
    expect(container.textContent).toContain("high");
  });
  it("shows empty", () => {
    const { container } = render(<Card forecasts={[]} appName="App" />);
    expect(container.textContent).toContain("No forecasts available");
  });
});
