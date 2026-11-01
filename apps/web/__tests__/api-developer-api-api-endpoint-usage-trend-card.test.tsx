import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiEndpointUsageTrendCard from "../src/components/api-developer-api-api-endpoint-usage-trend-card";

const trends = [
  { endpoint: "/api/users", total: 10000, avg_daily: 1000, trend_direction: "growing" },
  { endpoint: "/api/old", total: 500, avg_daily: 50, trend_direction: "declining" },
];

describe("APIDeveloperAPIApiEndpointUsageTrendCard", () => {
  it("shows trends", () => {
    const { container } = render(<APIDeveloperAPIApiEndpointUsageTrendCard trends={trends} growingCount={1} decliningCount={1} appName="App" />);
    expect(container.textContent).toContain("Usage Trends");
    expect(container.textContent).toContain("1 growing");
    expect(container.textContent).toContain("1 declining");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("1000/day");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiEndpointUsageTrendCard trends={[]} growingCount={0} decliningCount={0} appName="App" />);
    expect(container.textContent).toContain("No trend data");
  });
});
