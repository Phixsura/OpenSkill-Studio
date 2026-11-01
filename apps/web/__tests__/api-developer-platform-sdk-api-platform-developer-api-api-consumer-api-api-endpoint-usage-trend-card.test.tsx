import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-endpoint-usage-trend-card";

describe("EndpointUsageTrendCard", () => {
  it("shows trends", () => {
    const trends = [{ endpoint: "/users", method: "GET", trend: "growing", total_requests: 15000 }];
    const { container } = render(<Card trends={trends} growingCount={1} decliningCount={0} appName="App" />);
    expect(container.textContent).toContain("Usage Trends");
    expect(container.textContent).toContain("15,000");
  });
  it("shows empty", () => {
    const { container } = render(<Card trends={[]} growingCount={0} decliningCount={0} appName="App" />);
    expect(container.textContent).toContain("No trend data");
  });
});
