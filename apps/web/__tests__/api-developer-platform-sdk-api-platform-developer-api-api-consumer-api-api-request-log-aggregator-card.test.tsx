import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-log-aggregator-card";

describe("RequestLogAggregatorCard", () => {
  it("shows buckets", () => {
    const buckets = [{ bucket_key: "2024-01-15T14:00", request_count: 500, error_rate: 2.5, avg_latency: 45 }];
    const { container } = render(<Card buckets={buckets} totalRequests={5000} peakBucket="14:00" appName="App" />);
    expect(container.textContent).toContain("Log Aggregator");
    expect(container.textContent).toContain("5,000 total");
    expect(container.textContent).toContain("500");
  });
  it("shows empty", () => {
    const { container } = render(<Card buckets={[]} totalRequests={0} peakBucket="" appName="App" />);
    expect(container.textContent).toContain("No aggregated data");
  });
});
