import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiConsumerUsageTrendCard from "../src/components/api-developer-api-api-developer-api-api-consumer-usage-trend-card";

const trends = [
  { consumer_id: "acme", total: 50000, avg_daily: 5000, trend: "growing" },
  { consumer_id: "beta", total: 1000, avg_daily: 100, trend: "declining" },
];

describe("Card", () => {
  it("shows trends", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerUsageTrendCard trends={trends} growingCount={1} decliningCount={1} appName="App" />);
    expect(container.textContent).toContain("Consumer Trends");
    expect(container.textContent).toContain("1 growing");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("5000/day");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerUsageTrendCard trends={[]} growingCount={0} decliningCount={0} appName="App" />);
    expect(container.textContent).toContain("No trend data");
  });
});
