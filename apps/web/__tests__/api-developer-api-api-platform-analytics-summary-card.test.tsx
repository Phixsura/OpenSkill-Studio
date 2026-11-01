import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiPlatformAnalyticsSummaryCard from "../src/components/api-developer-api-api-platform-analytics-summary-card";

const summary = {
  total_requests_7d: 500000, total_requests_30d: 2000000, unique_consumers_7d: 200,
  avg_latency_ms: 45, p99_latency_ms: 200, error_rate_pct: 0.05,
  request_growth_pct: 15.5, consumer_growth_pct: 8.2,
  top_endpoint: "/api/users", top_consumer: "acme",
  webhook_delivery_rate_pct: 99.8, health_indicator: "excellent",
};

describe("APIDeveloperAPIApiPlatformAnalyticsSummaryCard", () => {
  it("shows analytics", () => {
    const { container } = render(<APIDeveloperAPIApiPlatformAnalyticsSummaryCard summary={summary} appName="App" />);
    expect(container.textContent).toContain("Platform Analytics");
    expect(container.textContent).toContain("EXCELLENT");
    expect(container.textContent).toContain("500,000");
    expect(container.textContent).toContain("+15.5%");
    expect(container.textContent).toContain("/api/users");
  });
});
