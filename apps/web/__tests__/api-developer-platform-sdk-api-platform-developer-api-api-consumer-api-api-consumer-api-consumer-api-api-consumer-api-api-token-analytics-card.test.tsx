import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-token-analytics-card";

describe("ConsumerApiTokenAnalyticsCard", () => {
  it("shows analytics", () => {
    const analytics = [{ tokenId: "t1", totalRequests: 5000, uniqueEndpoints: 8, uniqueIps: 3, errorCount: 10, lastUsed: "5m ago", topEndpoints: [["GET /api/users", 3000]] as [string, number][] }];
    const { container } = render(<Card analytics={analytics} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Token Analytics");
    expect(container.textContent).toContain("t1");
    expect(container.textContent).toContain("8 endpoints");
    expect(container.textContent).toContain("3 IPs");
  });
  it("shows empty", () => {
    const { container } = render(<Card analytics={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No token usage data");
  });
});
