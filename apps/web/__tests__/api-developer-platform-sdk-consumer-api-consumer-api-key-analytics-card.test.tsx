import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-api-key-analytics-card";

describe("ConsumerApiKeyAnalyticsCard", () => {
  it("shows key analytics", () => {
    const keys = [{ keyId: "k1", totalRequests: 5000, errorRate: 0.5, avgLatencyMs: 75, uniqueEndpoints: 8, lastUsed: "5m ago" }];
    const { container } = render(<Card keys={keys} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Key Analytics");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("0.5% err");
    expect(container.textContent).toContain("75ms avg");
  });
  it("shows empty", () => {
    const { container } = render(<Card keys={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No key usage data");
  });
});
