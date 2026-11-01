import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-usage-summary-card";

describe("ConsumerApiUsageSummaryCard", () => {
  it("shows summaries", () => {
    const summaries = [{ consumer_id: "c1", total_requests: 50000, success_rate: 99.5, avg_latency_ms: 42, unique_endpoints: 15, data_total_mb: 10.5 }];
    const { container } = render(<Card summaries={summaries} appName="App" />);
    expect(container.textContent).toContain("Consumer Usage");
    expect(container.textContent).toContain("50,000 reqs");
    expect(container.textContent).toContain("99.5%");
  });
  it("shows empty", () => {
    const { container } = render(<Card summaries={[]} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
