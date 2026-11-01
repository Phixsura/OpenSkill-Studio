import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-analytics-card";

describe("ConsumerApiAnalyticsCard", () => {
  it("shows summaries", () => {
    const summaries = [{ metric: "latency_ms", total: 5000, average: 125, min: 50, max: 300, points: 40, trend: "up" }];
    const { container } = render(<Card summaries={summaries} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("API Analytics");
    expect(container.textContent).toContain("latency_ms");
    expect(container.textContent).toContain("up");
    expect(container.textContent).toContain("Avg: 125");
  });
  it("shows empty", () => {
    const { container } = render(<Card summaries={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No analytics data");
  });
});
