import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-consumer-api-consumer-api-consumer-endpoint-usage-analytics-v2-card";

describe("EndpointUsageAnalyticsV2Card", () => {
  it("shows analytics", () => {
    const analytics = [{ endpoint: "/api/users", totalRequests: 10000, uniqueConsumers: 15, avgMs: 75, p95Ms: 300, errorRate: 0.5, rpm: 120, topConsumers: [["c1", 5000]] as [string, number][] }];
    const { container } = render(<Card analytics={analytics} appName="App" />);
    expect(container.textContent).toContain("Endpoint Analytics V2");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("75ms avg");
    expect(container.textContent).toContain("120 rpm");
    expect(container.textContent).toContain("15 consumers");
  });
  it("shows empty", () => {
    const { container } = render(<Card analytics={[]} appName="App" />);
    expect(container.textContent).toContain("No analytics data");
  });
});
