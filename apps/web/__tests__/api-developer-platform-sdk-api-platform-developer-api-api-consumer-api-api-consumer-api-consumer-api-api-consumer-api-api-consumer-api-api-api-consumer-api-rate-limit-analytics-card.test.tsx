import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-rate-limit-analytics-card";

describe("ConsumerApiRateLimitAnalyticsCard", () => {
  it("shows analytics", () => {
    const { container } = render(<Card consumerId="c1" totalRequests={10000} throttledCount={50} throttleRate={0.5} peakHour={14} mostThrottledEndpoint="/api/heavy" appName="App" />);
    expect(container.textContent).toContain("Rate Limit Analytics");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("0.5%");
    expect(container.textContent).toContain("14:00");
    expect(container.textContent).toContain("/api/heavy");
  });
  it("shows zero throttle", () => {
    const { container } = render(<Card consumerId="c1" totalRequests={100} throttledCount={0} throttleRate={0} peakHour={10} mostThrottledEndpoint="" appName="App" />);
    expect(container.textContent).toContain("0%");
  });
});
