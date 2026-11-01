import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdownCard from "../src/components/api-developer-api-api-developer-api-api-consumer-api-usage-breakdown-card";

const breakdowns = [{
  consumer_id: "acme", total_calls: 50000, total_errors: 150, unique_endpoints: 12,
  endpoints: [{ endpoint: "/api/users", method: "GET", call_count: 30000, error_count: 50 }],
}];

describe("Card", () => {
  it("shows breakdowns", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdownCard breakdowns={breakdowns} appName="App" />);
    expect(container.textContent).toContain("Usage Breakdown");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("50,000 calls");
    expect(container.textContent).toContain("12 endpoints");
    expect(container.textContent).toContain("150 errors");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdownCard breakdowns={[]} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
