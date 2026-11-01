import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-endpoint-usage-trend-card";

describe("EndpointUsageTrendCard", () => {
  it("shows trend", () => {
    const periods = [{ period: "2026-01", requests: 1000, errors: 5, avgMs: 50 }, { period: "2026-02", requests: 1500, errors: 3, avgMs: 45 }];
    const { container } = render(<Card endpointPath="/api/users" periods={periods} trendDirection="growing" growthRate={50} appName="App" />);
    expect(container.textContent).toContain("Usage Trend");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("growing");
    expect(container.textContent).toContain("+50%");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpointPath="/api" periods={[]} trendDirection="stable" growthRate={0} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
